"""
Copyright: (c) 2020, Michael Barthelmäs, Marcel Killinger, Johannes Keller
GNU General Public License v3.0 (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

This file is part of Telegram Survey Bot.

Telegram Survey Bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Telegram Survey Bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Telegram Survey Bot.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
from datetime import datetime, time
from random import randint
from typing import Callable, List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from bot_utils.bot_enums import SurveyType, EndUrlDistribution
from bot_utils.bot_utils import TimeSettings
from bot_utils.config import Config
from bot_utils.db_handler import DbHandler
from bot_utils.time_util import TimeUtil
from bot_utils.logging_strings import *


class BotScheduleError(Exception):
    pass


class ScheduleUtil:
    """
    Util class to schedule different jobs.
    """
    scheduler: BackgroundScheduler
    config: Config
    db_handler: DbHandler
    logger: logging

    def __init__(self, scheduler: BackgroundScheduler, config: Config, db_handler: DbHandler) -> None:
        """
        Constructor.

        :param scheduler: The BackgroundScheduler instance
        :param config: The Config instance
        :param db_handler: The DatabaseHandler instance
        """
        self.scheduler: BackgroundScheduler = scheduler
        self.config: Config = config
        self.db_handler: DbHandler = db_handler
        self.logger: logging = logging.getLogger(__name__)

    def schedule_delete_message(self, exec_function: Callable, delay_minutes: int, *func_args) -> None:
        """
        Schedules the deletion of messages, depending on the execution function.
        The deletion will be scheduled to run after the delay minutes from
        the time point of the execution of this function.

        :param exec_function: The function, which will delete the messages
        :param delay_minutes: The delay minutes until execution
        :param func_args: The arguments for the execution function
        :return: None
        """
        delete_datetime = TimeUtil.get_date_time_in(minutes=delay_minutes)
        self.schedule_delete_messages(exec_function, delete_datetime, *func_args)

    def schedule_delete_messages(self, exec_function: Callable, run_date: datetime, *func_args) -> None:
        """
        Schedules the deletion of messages, depending on the execution function.
        The deletion will be scheduled to run at the run date.

        :param exec_function: The function, which will delete the messages
        :param run_date: The date-time to execute the function
        :param func_args: The arguments for the execution function
        :return: None
        """
        trigger = DateTrigger(run_date=run_date)
        self.scheduler.add_job(exec_function,
                               trigger=trigger,
                               args=func_args)

    def schedule_end_survey_reminder(self,
                                     exec_function: Callable,
                                     subscriber_information: List[Tuple[int, int, int]]) -> None:
        """
        Schedules the end survey reminder.

        :param exec_function: The execution function to send the end survey reminder
        :param subscriber_information: The subscriber information list
        :return: None
        """
        run_date = TimeUtil.get_date_time_in(hours=self.config.endSurveyReminderDelayHours)
        date_str = run_date.strftime("%Y-%m-%d-%H:%M")
        trigger = DateTrigger(run_date=run_date)
        self.scheduler.add_job(exec_function,
                               trigger=trigger,
                               args=[[chat_id for chat_id, _, _ in subscriber_information], date_str])
        self.db_handler.insert_end_reminder_entries_from_list(SurveyType.END, subscriber_information, date_str)

    def add_jobs_from_list(self, datetime_list: List[datetime], exec_function: Callable, survey_type: SurveyType) \
            -> None:
        """
        Add multiple jobs (one for every datetime in datetime_list) to the scheduler instance.

        :param datetime_list: The datetime list
        :param exec_function: The function to run on job execution
        :param survey_type: The survey type
        :return: None
        """
        for date in datetime_list:
            job_id = date.strftime("%Y-%m-%d-%H:%M") + survey_type.name
            if self.scheduler.get_job(job_id) is None:
                self.add_job(date, exec_function, survey_type)

    def add_job(self, date: datetime, exec_function: Callable, survey_type: SurveyType) -> None:
        """
        Adds a single job with an execution function. Job will be executed at the date.

        :param date: The execution date of the job
        :param exec_function: The function to run at job execution
        :param survey_type: The survey type
        :return: None
        """
        if survey_type == SurveyType.DAILY:
            jitter = self.config.randomTimeShiftSettings.daily_RandomTimeShiftMinutes * 60
        else:
            jitter = self.config.randomTimeShiftSettings.end_RandomTimeShiftMinutes * 60
        job_id = date.strftime("%Y-%m-%d-%H:%M") + survey_type.name
        self.logger.info(SU_ADD_JOB.format(job_id))
        date_str = date.strftime("%Y-%m-%d-%H:%M")
        trigger = CronTrigger(year=date.year,
                              month=date.month,
                              day=date.day,
                              hour=date.hour,
                              minute=date.minute,
                              jitter=jitter)
        job = self.scheduler.add_job(exec_function,
                                     trigger=trigger,
                                     args=[survey_type, job_id, date_str],
                                     id=job_id)

    def add_new_subscriber(self,
                           chat_id: int,
                           condition: int,
                           exec_function: Callable,
                           wakeup_time: time = None) -> None:
        """
        Adds a new subscriber with his condition.


        :param chat_id: The chat id of the new subscriber
        :param condition: The condition of the new subscriber
        :param exec_function: The execution funktion (send_broadcast_message)
        :param wakeup_time: The wakeup time of the new subscriber
        :return: None
        """
        time_offset = self.db_handler.get_time_offset(chat_id)
        daily_dates = self.__calculate_date_list(SurveyType.DAILY)
        end_dates = self.__calculate_date_list(SurveyType.END)
        daily_date_times = self.__calculate_date_time_list(daily_dates, wakeup_time, SurveyType.DAILY, time_offset)
        end_date_times = self.__calculate_date_time_list(end_dates, wakeup_time, SurveyType.END, time_offset)
        end_distribution_list = self.calculate_end_distribution(end_date_times)

        self.db_handler.insert_new_subscriber_entries(chat_id,
                                                      daily_date_times,
                                                      SurveyType.DAILY,
                                                      condition)
        self.db_handler.insert_new_subscriber_entries(chat_id,
                                                      end_date_times,
                                                      SurveyType.END,
                                                      condition,
                                                      end_distribution_list)
        self.add_jobs_from_list(daily_date_times, exec_function, SurveyType.DAILY)
        self.add_jobs_from_list(end_date_times, exec_function, SurveyType.END)

    def __calculate_date_list(self, survey_type: SurveyType) -> List[datetime]:
        """
        Calculates a list of survey dates depending on the given config and survey_type.

        :param survey_type: The survey type
        :return: List of dates (List[datetime])
        """
        if not self.config.useDayCalculation:
            if survey_type == SurveyType.DAILY:
                return self.config.daily_dates
            if survey_type == SurveyType.END:
                return self.config.end_dates
        else:
            if survey_type == SurveyType.DAILY:
                return TimeUtil.generate_date_list(self.config.dayCalculationSettings.daily_SurveyDays)
            if survey_type == SurveyType.END:
                return TimeUtil.generate_date_list(self.config.dayCalculationSettings.end_SurveyDays)

    def __calculate_date_time_list(self,
                                   dates: List[datetime],
                                   wakeup_time: time,
                                   survey_type: SurveyType,
                                   offset: int) -> List[datetime]:
        """
        Calculates the survey times and add them to the dates list.

        :param dates: the date list
        :param wakeup_time: the wakeup time
        :param survey_type: the survey type
        :param offset: the time zone offset
        :return: List of dates with time (List[datetime])
        """
        if not self.config.useTimeCalculation:
            if survey_type == SurveyType.DAILY:
                return TimeUtil.generate_date_time_list(dates, self.config.daily_times, offset)
            if survey_type == SurveyType.END:
                return TimeUtil.generate_date_time_list(dates, self.config.end_times, offset)
        else:
            if survey_type == SurveyType.DAILY:
                time_settings = TimeSettings(wakeup_time,
                                             self.config.timeCalculationSettings.daily_DelayMinutesAfterWakeup,
                                             self.config.timeCalculationSettings.daily_SurveysPerDay,
                                             self.config.timeCalculationSettings.daily_DelayMinutesBetweenSurveys)
                return TimeUtil.generate_date_time_list(dates, time_settings,offset)
            if survey_type == SurveyType.END:
                time_settings = TimeSettings(wakeup_time,
                                             self.config.timeCalculationSettings.end_DelayMinutesAfterWakeup,
                                             self.config.timeCalculationSettings.end_SurveysPerDay,
                                             self.config.timeCalculationSettings.end_DelayMinutesBetweenSurveys)
                return TimeUtil.generate_date_time_list(dates, time_settings, offset)

    def calculate_end_distribution(self, end_list: List[datetime]) -> List[int]:
        """
        Calculates the end distribution list, depending on the strategy in the config file.

        :param end_list: List of end survey datetimes
        :return: List with the end  (List[int])
        """
        end_distribution_list: List[int] = []
        last_day: int = end_list[0].day
        count = 0
        if self.config.urls.end_url_distribution == EndUrlDistribution.NONE:
            return [0] * len(end_list)
        elif self.config.urls.end_url_distribution == EndUrlDistribution.DAY:
            for date in end_list:
                if last_day != date.day:
                    count += 1
                    last_day = date.day
                end_distribution_list.append(count)
            return end_distribution_list
        elif self.config.urls.end_url_distribution == EndUrlDistribution.TIME:
            for date in end_list:
                if last_day != date.day:
                    count = 0
                    last_day = date.day
                end_distribution_list.append(count)
                count += 1
            return end_distribution_list
        elif self.config.urls.end_url_distribution == EndUrlDistribution.MIXED:
            return list(range(len(end_list)))
        else:
            for _ in end_list:
                end_distribution_list.append(randint(0, len(self.config.urls.end_url[0]) - 1))
            return end_distribution_list
