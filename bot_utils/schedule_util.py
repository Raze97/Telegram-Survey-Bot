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
from datetime import datetime, time
from random import randint
from typing import Callable, List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from bot_utils.bot_enums import SurveyType, EndUrlDistribution
from bot_utils.bot_util_types import TimeSettings
from bot_utils.config import Config
from bot_utils.db_handler import DbHandler
from bot_utils.time_util import TimeUtil


class BotScheduleError(Exception):
    pass


class ScheduleUtil:
    """
    Util class to schedule different jobs.
    """
    scheduler: BackgroundScheduler
    config: Config
    db_handler: DbHandler

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

    def schedule_delete_message(self, exec_function: Callable, delay_minutes: int, *func_args) -> None:
        """
        Schedules the deletion of messages, depending on the execution function.
        The deletion will be scheduled to run after the delay minutes from
        the time point of the execution of this function.

        :param exec_function: The function, which will delete the messages
        :param delay_minutes: The delay minutes until execution
        :param func_args: The arguments for the execution function
        :return:
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
        :return:
        """
        trigger = DateTrigger(run_date=run_date)
        self.scheduler.add_job(exec_function,
                               trigger=trigger,
                               args=func_args)

    def schedule_surveys(self, exec_function: Callable, survey_type: SurveyType) -> None:
        """
        Generates a datetime list and add all elements to the scheduler.

        :param exec_function: Execution function to send the surveys
        :param survey_type: The survey type
        :raises BotScheduleError: when survey type is SUBSCRIBE
        :return: None
        """
        if survey_type == SurveyType.DAILY:
            time_list = self.config.daily_times
            day_list = self.config.daily_dates
            survey_days = self.config.dayCalculationSettings.daily_SurveyDays
        elif survey_type == SurveyType.END:
            time_list = self.config.end_times
            day_list = self.config.end_dates
            survey_days = self.config.dayCalculationSettings.end_SurveyDays
        else:
            raise BotScheduleError("SUBSCRIBE surveys can not be scheduled.")

        if not self.config.useDayCalculation and not self.config.useTimeCalculation:
            datetime_list: List[datetime] = TimeUtil.generate_date_time_list(day_list,
                                                                             time_list)

            self.add_jobs_from_list(datetime_list, exec_function, survey_type)

        elif self.config.useDayCalculation and not self.config.useTimeCalculation:
            date_list = TimeUtil.generate_date_list(self.config.subscription_start_date,
                                                    self.config.subscription_deadline,
                                                    survey_days,
                                                    time_list)

            self.add_jobs_from_list(date_list, exec_function, survey_type)

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
            jitter = self.config.randomTimeShiftSettings.daily_RandomTimeShiftMinutes
        else:
            jitter = self.config.randomTimeShiftSettings.end_RandomTimeShiftMinutes
        job_id = date.strftime("%Y-%m-%d-%H:%M") + survey_type.name
        date_str = date.strftime("%Y-%m-%d-%H:%M")
        trigger = CronTrigger(year=date.year,
                              month=date.month,
                              day=date.day,
                              hour=date.hour,
                              minute=date.minute,
                              jitter=jitter)
        self.scheduler.add_job(exec_function,
                               trigger=trigger,
                               args=[survey_type, job_id, date_str],
                               id=job_id)

    def add_subscriber(self, chat_id: int, condition: int) -> bool:
        """
        Adds a new subscriber if time calculation is not activated.
        All survey datetimes are calculated and entries in the database will be inserted.

        :param chat_id: The chat id
        :param condition: The condition
        :return: If all works are done, false when time calculation is activated
        """
        if self.config.useTimeCalculation or self.config.useTimeZoneCalculation:
            return False
        else:
            if not self.config.useDayCalculation:
                daily_list = TimeUtil.generate_date_time_list(self.config.daily_dates, self.config.daily_times)

                self.db_handler.insert_new_subscriber_entries(chat_id, daily_list, SurveyType.DAILY, condition)

                end_list: List[datetime] = TimeUtil.generate_date_time_list(self.config.end_dates,
                                                                            self.config.end_times)
                end_distribution_list: List[int] = self.calculate_end_distribution(end_list)
                self.db_handler.insert_new_subscriber_entries(chat_id,
                                                              end_list,
                                                              SurveyType.END,
                                                              condition,
                                                              end_distribution_list=end_distribution_list)

                return True
            else:
                daily_list = TimeUtil \
                    .generate_date_list_for_subscriber_day_calc(self.config.dayCalculationSettings.daily_SurveyDays,
                                                                self.config.daily_times)
                self.db_handler.insert_new_subscriber_entries(chat_id, daily_list, SurveyType.DAILY, condition)

                end_list = TimeUtil \
                    .generate_date_list_for_subscriber_day_calc(self.config.dayCalculationSettings.end_SurveyDays,
                                                                self.config.end_times)
                end_distribution_list: List[int] = self.calculate_end_distribution(end_list)
                self.db_handler.insert_new_subscriber_entries(chat_id,
                                                              end_list,
                                                              SurveyType.END,
                                                              condition,
                                                              end_distribution_list=end_distribution_list)
                return True

    def add_subscriber_time_calculated(self,
                                       chat_id: int,
                                       condition: int,
                                       wakeup_time: time,
                                       exec_function: Callable) -> None:
        """
        Add all subscriber entries to the job queue and database with time calculation.

        :param chat_id: The chat id
        :param condition: The condition
        :param wakeup_time: The wakeup time
        :param exec_function: The execution function for the jobs
        :return: None
        """
        daily_settings = TimeSettings(wakeup_time,
                                      self.config.timeCalculationSettings.daily_DelayMinutesAfterWakeup,
                                      self.config.timeCalculationSettings.daily_SurveysPerDay,
                                      self.config.timeCalculationSettings.daily_DelayMinutesBetweenSurveys)
        end_settings = TimeSettings(wakeup_time,
                                    self.config.timeCalculationSettings.end_DelayMinutesAfterWakeup,
                                    self.config.timeCalculationSettings.end_SurveysPerDay,
                                    self.config.timeCalculationSettings.end_DelayMinutesBetweenSurveys)
        if self.config.useDayCalculation:
            daily_list = self.generate_date_list_and_add_to_db(self.config.dayCalculationSettings.daily_SurveyDays,
                                                               daily_settings,
                                                               chat_id,
                                                               SurveyType.DAILY,
                                                               condition)
            self.add_jobs_from_list(daily_list, exec_function, SurveyType.DAILY)

            end_list = self.generate_date_list_and_add_to_db(self.config.dayCalculationSettings.end_SurveyDays,
                                                             end_settings,
                                                             chat_id,
                                                             SurveyType.END,
                                                             condition)
            self.add_jobs_from_list(end_list, exec_function, SurveyType.END)
        else:
            daily_list = TimeUtil.generate_date_list_for_subscriber(self.config.daily_dates, daily_settings)
            end_list = TimeUtil.generate_date_list_for_subscriber(self.config.end_dates, end_settings)
            end_distribution_list = self.calculate_end_distribution(end_list)
            self.db_handler.insert_new_subscriber_entries(chat_id, daily_list, SurveyType.DAILY, condition)
            self.db_handler.insert_new_subscriber_entries(chat_id,
                                                          end_list,
                                                          SurveyType.END,
                                                          condition,
                                                          end_distribution_list=end_distribution_list)
            self.add_jobs_from_list(daily_list, exec_function, SurveyType.DAILY)
            self.add_jobs_from_list(end_list, exec_function, SurveyType.END)

    def generate_date_list_and_add_to_db(self,
                                         survey_days: List[int],
                                         time_settings: TimeSettings,
                                         chat_id: int,
                                         survey_type: SurveyType,
                                         condition: int) -> List[datetime]:
        """
        Generates a datetime list and insert the entries to the database.

        :param survey_days: The survey days array from the config
        :param time_settings: The time settings object
        :param chat_id: The chat id
        :param survey_type: The survey type
        :param condition: The condition
        :return: List of the generated datetimes
        """
        day_list = TimeUtil \
            .generate_date_list_for_subscriber_day_calc(survey_days,
                                                        time_settings)
        if survey_type == SurveyType.END:
            end_distribution_list = self.calculate_end_distribution(day_list)
            self.db_handler.insert_new_subscriber_entries(chat_id,
                                                          day_list,
                                                          survey_type,
                                                          condition,
                                                          end_distribution_list=end_distribution_list)
        else:
            self.db_handler.insert_new_subscriber_entries(chat_id, day_list, survey_type, condition)
        return day_list

    def calculate_end_distribution(self, end_list: List[datetime]) -> List[int]:
        """
        Calculates the end distribution list, depending on the strategy in the config file.

        :param end_list: List of end survey datetimes
        :return: List with the end indexes
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
