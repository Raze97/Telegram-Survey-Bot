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
from datetime import datetime, timedelta, time as Time
from typing import List, Union

from bot_utils.bot_util_types import TimeSettings


class TimeUtil:
    """
    Helper class for time calculations and parsing.
    """

    @staticmethod
    def get_time_from_str(time_str: str) -> Time:
        """
        Convers an string with the format "HH:MM" to a time instance

        :param time_str: The time string
        :return: The time instance
        """
        number_strings: List[str] = time_str.split(":")
        hour: int = int(number_strings[0])
        minute: int = int(number_strings[1])
        return Time(hour=hour, minute=minute)

    @staticmethod
    def get_date_time(date: datetime, time: Time) -> datetime:
        """
        Combines a datetime and a time instance to one datetime instance.
        Therefor the time from the time instance and the year, month and day values from the date are used.

        :param date: The date
        :param time: The time
        :return: The combined datetime
        """
        return datetime(date.year, date.month, date.day, time.hour, time.minute)

    @staticmethod
    def get_date_time_in(start_time: datetime = None, hours=0, minutes=0, seconds=0) -> datetime:
        """
        Calculates the datetime in a specific future from a specific time-point.

        :param start_time: The start time point (default: datetime.now())
        :param hours: The hours in future (default: 0)
        :param seconds: The minutes in future (default: 0)
        :param minutes: The seconds in future (default: 0)
        :return: datetime in specific future
        """
        if start_time is None:
            start_time = datetime.now()
        start_time += timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return start_time

    @staticmethod
    def generate_date_time_list(dates: List[datetime], times: List[List[Time]]) -> List[datetime]:
        """
        Generates a list of datetime instances from a list of date-strings and a list of time-strings.

        :param dates: the list of date-strings
        :param times: the list of time-strings
        :return: the list of datetime instances
        """
        dt_list: List[datetime] = []
        for i, date in enumerate(dates):
            for time in times[i]:
                date_time: datetime = TimeUtil.get_date_time(date, time)
                dt_list.append(date_time)
        return dt_list

    @staticmethod
    def generate_date_list(subscription_start_date: datetime,
                           subscription_deadline: datetime,
                           day_list: List[int],
                           time_list: List[List[Time]]) -> List[datetime]:
        """

        :param subscription_start_date:
        :param subscription_deadline:
        :param day_list:
        :param time_list:
        :return:
        """
        date_list: List[datetime] = []

        for i, times in enumerate(time_list):
            first_date = subscription_start_date + timedelta(days=day_list[i])
            last_date = subscription_deadline + timedelta(days=day_list[i])
            while first_date <= last_date:
                for time_str in times:
                    date_time = TimeUtil.get_date_time(first_date, time_str)
                    date_list.append(date_time)
                first_date += timedelta(days=1)

        date_list = list(set(date_list))
        date_list.sort()
        return date_list

    @staticmethod
    def generate_date_list_for_subscriber(day_list: List[datetime],
                                          time_settings: TimeSettings) -> List[datetime]:
        """
        Generates a datetime list from a date list and the time settings.

        :param day_list: The date list
        :param time_settings: The time settings
        :return: List with all datetimes
        """
        date_list: List[datetime] = []
        for date in day_list:
            date_list.extend(TimeUtil.add_dates(date, time_settings))
        return date_list

    @staticmethod
    def generate_date_list_for_subscriber_day_calc(day_list: List[int],
                                                   time_settings: Union[List[List[Time]], TimeSettings]) \
            -> List[datetime]:
        """
        Generates a datetime list from a day list and a time list or a time settings instance.

        :param day_list: The day list
        :param time_settings: The time list or the time settings instance
        :return: List with all datetimes
        """
        date_list: List[datetime] = []
        today: datetime = datetime.now()
        if isinstance(time_settings, TimeSettings):
            for day_delta in day_list:
                date = today + timedelta(days=day_delta)
                date_list.extend(TimeUtil.add_dates(date, time_settings))
        else:
            for i, times in enumerate(time_settings):
                date = today + timedelta(days=day_list[i])
                for time_str in times:
                    date_time = TimeUtil.get_date_time(date, time_str)
                    date_list.append(date_time)

        return date_list

    @staticmethod
    def add_dates(date: datetime, time_settings: TimeSettings) -> List[datetime]:
        """
        Generates a datetime list from a specific date and timesettings.

        :param date: The date
        :param time_settings: The time settings.
        :return: List of all datetimes
        """
        date_list: List[datetime] = []
        date = TimeUtil.get_date_time(date, time_settings.wakeup_time)
        for i in range(time_settings.survey_count):
            if i == 0:
                date += timedelta(minutes=time_settings.delay_minutes_after_wakeup)
                date_list.append(date)
            else:
                date += timedelta(minutes=time_settings.delay_minutes_between_surveys)
                date_list.append(date)
        return date_list

    @staticmethod
    def get_time_offset(participant_datetime: datetime) -> int:
        datetime_now = datetime.now().replace(second=0, microsecond=0)
        timedelta_to_participant = datetime_now - participant_datetime

        return 0
