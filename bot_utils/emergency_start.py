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
from datetime import datetime
from typing import List, Tuple, Callable

from readchar import readchar

from bot_utils.bot_enums import SurveyType
from bot_utils.bot_utils import destruct_tuple
from bot_utils.db_handler import DbHandler
from bot_utils.logging_strings import *
from bot_utils.schedule_util import ScheduleUtil

KEY_Y = b"y"
KEY_N = b"n"


class EmergencyStart:
    """
    Class for the Emergency-Start.
    """
    scheduler: ScheduleUtil
    db_handler: DbHandler
    logger: logging

    def __init__(self, scheduler: ScheduleUtil, db_handler: DbHandler, exec_function: Callable) -> None:
        """
        Constructor.\n
        After initializing all fields, this constructor will automatically run the check, if an emergency-start
        is possible.

        :param scheduler: the schedule util instance
        :param db_handler: the database handler instance
        :param exec_function: the send notification broadcast function of the bot main file
        """
        self.schedule_util = scheduler
        self.db_handler = db_handler
        self.logger = logging.getLogger(__name__)
        self.progress(exec_function)

    def progress(self, exec_function: Callable) -> None:
        """
        Handles the whole emergency-start progress.

        :param exec_function: the send notification broadcast function of the bot main file
        :return: None
        """
        future_dates: List[Tuple[datetime, SurveyType]] = list(dict.fromkeys(self.get_future_survey_dates()))
        if future_dates:
            if self.ask_for_emergency_start(len(future_dates)):
                self.restore_scheduler_entries(future_dates, exec_function)
            else:
                if self.ask_for_database_cleanup():
                    self.db_handler.delete_all_subscribers()
                    self.logger.info(EMERGENCY_DATES_IGNORE_DELETE.format(len(future_dates)))
                else:
                    self.logger.info(EMERGENCY_DATES_IGNORE.format(len(future_dates)))

    def get_future_survey_dates(self) -> List[Tuple[datetime, SurveyType]]:
        """
        Queries all survey dates in the database pick the future dates out to reschedule them.

        :return: list of future dates tuples (datetime, SurveyType)
        """
        tuple_list: List[Tuple[datetime, SurveyType]] = self.db_handler.query_subscribers_emergency_start()
        datetime_now = datetime.now()
        return list(filter(destruct_tuple(lambda dt, _: datetime_now < dt), tuple_list))

    def ask_for_emergency_start(self, count_future_dates: int) -> bool:
        """
        Prompts a message to the command line, which asks the user if he wants to reschedule the future survey dates.

        :param count_future_dates: Count of the future dates
        :return: if the user has pressed yes or no (bool)
        """
        self.logger.warning(EMERGENCY_DATES_FOUND.format(count_future_dates))
        input_char = readchar()
        if input_char == KEY_Y or input_char == KEY_N:
            return input_char == KEY_Y
        else:
            return self.ask_for_emergency_start(count_future_dates)

    def ask_for_database_cleanup(self) -> bool:
        """
        Prompts a message to the command line, which asks the user if he wants to to clean all current entries in the
        database.

        :return: if the user has pressed yes or no (bool)
        """
        self.logger.warning(EMERGENCY_DATES_WARN)
        input_char = readchar()
        if input_char == KEY_Y or input_char == KEY_N:
            return input_char == KEY_Y
        else:
            return self.ask_for_database_cleanup()

    def restore_scheduler_entries(self,
                                  future_dates: List[Tuple[datetime, SurveyType]],
                                  exec_function: Callable) -> None:
        """
        Reschedules all entries of the given future dates list with the send_message_broadcast function
        (given as exec_function parameter).

        :param future_dates: the send notification broadcast function of the bot main file
        :param exec_function: the send notification broadcast function of the bot main file
        :return: None
        """
        self.logger.info(EMERGENCY_DATES_RESCHEDULE.format(len(future_dates)))
        for date, survey_type in future_dates:
            self.schedule_util.add_job(date, exec_function, survey_type)
