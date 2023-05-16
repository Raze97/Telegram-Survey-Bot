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

from bot_utils.bot_utils import TimeSettings

FIVE_MINUTES_SECONDS = 300


class TimeUtil:
    """
    Helper class for time calculations and parsing.
    """

    @staticmethod
    def get_time_from_str(time_str: str) -> Time:
        """
        Converts an string with the format "HH:MM" to a time instance

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
        Therefore the time from the time instance and the year, month and day values from the date are used.

        :param date: The date
        :param time: The time
        :return: The combined datetime
        """
        return datetime(date.year, date.month, date.day, time.hour, time.minute)

    @staticmethod
    def apply_time_offset(date_time: datetime, offset: int) -> datetime:
        """
        Applies the time zone offset to the given datetime object.

        :param date_time: the date time object
        :param offset: the time zone offset
        :return: the updated datetime
        """
        date_time += timedelta(seconds=offset)
        return date_time

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
    def generate_date_list(day_list: List[int]) -> List[datetime]:
        """
        Generates a date list from a given integer list.

        :param day_list: the integer list
        :return: the datetime list
        """
        date_list: List[datetime] = []
        today: datetime = datetime.now()
        for day_delta in day_list:
            date = today + timedelta(days=day_delta)
            date_list.append(date)
        return date_list

    @staticmethod
    def generate_time_list(day_count: int, time_settings: TimeSettings) -> List[List[Time]]:
        """
        Generates a list of time list depending on the day count and the time settings.

        :param day_count: the day count
        :param time_settings: the time settings
        :return: the list of time lists
        """
        times_list: List[Time] = []
        time_var: Time = time_settings.wakeup_time
        for i in range(time_settings.survey_count):
            if i == 0:
                time_var += timedelta(minutes=time_settings.delay_minutes_after_wakeup)
                times_list.append(time_var)
            else:
                time_var += timedelta(minutes=time_settings.delay_minutes_between_surveys)
                times_list.append(time_var)
        return [times_list] * day_count

    @staticmethod
    def generate_date_time_list(dates: List[datetime],
                                times: Union[List[List[Time]], TimeSettings],
                                offset: int = 0) -> List[datetime]:
        """
        Generates a list of datetime instances from a list of date-strings and a list of time-strings.

        :param dates: the list of date-strings
        :param times: the list of time-strings
        :param offset: the time offset
        :return: the list of datetime instances
        """
        dt_list: List[datetime] = []
        for i, date in enumerate(dates):
            if isinstance(times, TimeSettings):
                time_var: datetime = TimeUtil.get_date_time(date, times.wakeup_time)
                for j in range(times.survey_count):
                    if j == 0:
                        time_var += timedelta(minutes=times.delay_minutes_after_wakeup)
                        dt_list.append(time_var)
                    else:
                        time_var += timedelta(minutes=times.delay_minutes_between_surveys)
                        dt_list.append(time_var)
            else:
                for time in times[i]:
                    date_time: datetime = TimeUtil.get_date_time(date, time)
                    dt_list.append(date_time)
        if offset != 0:
            dt_list = list(map(lambda dt: TimeUtil.apply_time_offset(dt, offset), dt_list))
        return dt_list

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
        """
        Calculates the time zone offset with the given datetime.

        :param participant_datetime: the datetime of the participant
        :return: the time zone offset (int)
        """
        datetime_now = datetime.now().replace(second=0, microsecond=0)
        if datetime_now < participant_datetime:
            timedelta_to_participant: timedelta = participant_datetime - datetime_now
            timedelta_seconds = timedelta_to_participant.seconds
        else:
            timedelta_to_participant: timedelta = datetime_now - participant_datetime
            timedelta_seconds = -timedelta_to_participant.seconds

        if -FIVE_MINUTES_SECONDS <= timedelta_seconds <= FIVE_MINUTES_SECONDS:
            return 0
        else:
            return timedelta_seconds
