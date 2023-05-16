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
from typing import List

from bot_utils.bot_enums import EndUrlDistribution
from bot_utils.config import Config


class ConfigValidationException(Exception):
    """
    Exception for config validation errors.
    """
    message_list: List[str]

    def __init__(self, message_list: List[str]):
        """
        Constructor.

        :param message_list: list with error messages
        """
        self.message_list = message_list


class ConfigValidator:
    """
    Util class for config validation.
    """

    @staticmethod
    def validate_config(config: Config) -> None:
        """
        Validates a config instance.

        :raises ConfigValidationException: When config is not valid
        :param config: the config instance
        :return: None
        """
        error_list: List[str] = []
        error_list.extend(ConfigValidator.validate_dates_and_times(config))
        error_list.extend(ConfigValidator.validate_link_deletion_settings(config))
        error_list.extend(ConfigValidator.validate_urls(config))
        if error_list:
            raise ConfigValidationException(error_list)

    @staticmethod
    def validate_dates_and_times(config: Config) -> List[str]:
        """
        Validates all dates and times in the config.

        :param config: The config instance
        :return: The List of error messages. Empty when there are no errors
        """
        error_list: List[str] = []
        if config.subscription_start_date > config.subscription_deadline:
            error_list.append("subscription start date is after subscription deadline")
        if not config.useDayCalculation and not config.useTimeCalculation:
            if len(config.daily_dates) < len(config.daily_times):
                error_list.append("Not enough dates in 'daily_dates' to match number of time lists in 'daily_times'.")
            if len(config.end_dates) < len(config.end_times):
                error_list.append("Not enough dates in 'end_dates' to match number of time lists in 'end_times'.")
            if len(config.daily_times) < len(config.daily_dates):
                error_list.append("Not enough time lists in 'daily_times' to match number of dates in 'daily_dates'.")
            if len(config.end_times) < len(config.end_dates):
                error_list.append("Not enough time lists in 'end_times' to match number of dates in 'end_dates'.")
        if config.useDayCalculation and not config.useTimeCalculation:
            if len(config.dayCalculationSettings.daily_SurveyDays) < len(config.daily_times):
                error_list.append("Not enough dates in 'dayCalculationSettings.daily_SurveyDays' to match number of "
                                  "time lists in 'daily_times'.")
            if len(config.daily_times) < len(config.dayCalculationSettings.daily_SurveyDays):
                error_list.append("Not enough time lists in 'daily_times' to match number of "
                                  "dates in 'dayCalculationSettings.daily_SurveyDays'.")
            if len(config.dayCalculationSettings.end_SurveyDays) < len(config.end_times):
                error_list.append("Not enough dates in 'dayCalculationSettings.end_SurveyDays' to match number of "
                                  "time lists in 'end_times'.")
            if len(config.end_times) < len(config.dayCalculationSettings.end_SurveyDays):
                error_list.append("Not enough time lists in 'end_times' to match number of "
                                  "dates in 'dayCalculationSettings.end_SurveyDays'.")
        if config.useTimeCalculation:
            if config.timeCalculationSettings.daily_DelayMinutesAfterWakeup <= 0:
                error_list.append("'timeCalculationSettings.daily_DelayMinutesAfterWakeup' must be greater than 0")
            if config.timeCalculationSettings.daily_SurveysPerDay <= 0:
                error_list.append("'timeCalculationSettings.daily_SurveysPerDay' must be greater than 0")
            if not config.timeCalculationSettings.daily_SurveysPerDay == 1 and \
                    config.timeCalculationSettings.daily_DelayMinutesBetweenSurveys <= 0:
                error_list.append("'timeCalculationSettings.daily_DelayMinutesBetweenSurveys' must be greater than 0")
            if config.timeCalculationSettings.end_DelayMinutesAfterWakeup <= 0:
                error_list.append("'timeCalculationSettings.end_DelayMinutesAfterWakeup' must be greater than 0")
            if config.timeCalculationSettings.end_SurveysPerDay < 0:
                error_list.append("'timeCalculationSettings.end_SurveysPerDay' must be greater or equal than 0")
            if not (0 <= config.timeCalculationSettings.end_SurveysPerDay <= 1) and \
                    config.timeCalculationSettings.end_DelayMinutesBetweenSurveys <= 0:
                error_list.append("'timeCalculationSettings.end_DelayMinutesBetweenSurveys' must be greater than 0")
        return error_list

    @staticmethod
    def validate_link_deletion_settings(config: Config) -> List[str]:
        """
        Validates the link deletion settings.

        :param config: The config instance
        :return: The List of error messages. Empty when there are no errors
        """
        error_list: List[str] = []
        if config.linkDeletionSettings.start_DeleteLinkTimer and \
                config.linkDeletionSettings.start_DeleteDelayMinutes <= 0:
            error_list.append("'linkDeletionSettings.start_DeleteDelayMinutes' must be greater than 0")
        if config.linkDeletionSettings.daily_DeleteLinkTimer and \
                config.linkDeletionSettings.daily_DeleteDelayMinutes <= 0:
            error_list.append("'linkDeletionSettings.daily_DeleteDelayMinutes' must be greater than 0")
        if config.linkDeletionSettings.end_DeleteLinkTimer and \
                config.linkDeletionSettings.end_DeleteDelayMinutes <= 0:
            error_list.append("'linkDeletionSettings.end_DeleteDelayMinutes' must be greater than 0")
        if config.endSurveyReminderEnabled and config.endSurveyReminderDelayHours <= 0:
            error_list.append("'endSurveyReminderDelayHours' must be greater than 0")
        return error_list

    @staticmethod
    def validate_urls(config: Config) -> List[str]:
        """
        Validates the urls.

        :param config: The config instance
        :return: The List of error messages. Empty when there are no errors
        """
        error_list: List[str] = []
        len_start = len(config.urls.start_url)
        len_daily = len(config.urls.daily_url)
        len_end = len(config.urls.end_url)
        if not (len_start == len_daily == len_end):
            error_list.append("Different count of conditions found in urls section.")
        if config.urls.end_url_distribution == EndUrlDistribution.TIME:
            if config.useTimeCalculation:
                time_count = config.timeCalculationSettings.end_SurveysPerDay
                for i, condition_links in enumerate(config.urls.end_url, start=1):
                    if len(condition_links) != time_count:
                        msg = "Different count of links found at position " + str(i) \
                              + "in 'end_url', while 'end_SurveysPerDay' are " + str(time_count)
                        error_list.append(msg)
            else:
                it = iter(config.end_times)
                len_fst = len(next(it))
                if not all(len(l) == len_fst for l in it):
                    msg = "Different count of times found in 'end_times'"
                    error_list.append(msg)
                else:
                    for i, condition_links in enumerate(config.urls.end_url, start=1):
                        if len(condition_links) != len_fst:
                            msg = "Different count of links found at position " + str(i) \
                                  + " in 'end_url', while lenght of 'end_times' are " + str(len_fst)
                            error_list.append(msg)
        elif config.urls.end_url_distribution == EndUrlDistribution.DAY:
            if config.useDayCalculation:
                day_count = len(config.dayCalculationSettings.end_SurveyDays)
                for i, condition_links in enumerate(config.urls.end_url, start=1):
                    if len(condition_links) != day_count:
                        msg = "Different count of links found at position " + str(i) \
                              + " in 'end_url', while number of days in 'end_SurveyDays' are " + str(day_count)
                        error_list.append(msg)
            else:
                day_count = len(config.end_dates)
                for i, condition_links in enumerate(config.urls.end_url, start=1):
                    if len(condition_links) != day_count:
                        msg = "Different count of links found at position " + str(i) \
                              + " in 'end_url', while number of days in 'end_dates' are " + str(day_count)
                        error_list.append(msg)
        elif config.urls.end_url_distribution == EndUrlDistribution.MIXED:
            if not config.useTimeCalculation:
                count = sum([len(list_elem) for list_elem in config.end_times])
            else:
                if config.useDayCalculation:
                    count = config.timeCalculationSettings.end_SurveysPerDay * \
                            len(config.dayCalculationSettings.end_SurveyDays)
                else:
                    count = config.timeCalculationSettings.end_SurveysPerDay * \
                            len(config.end_dates)
            for i, condition_links in enumerate(config.urls.end_url, start=1):
                if len(condition_links) != count:
                    msg = "Different count of links found at position " + str(i) \
                          + " in 'end_url', while number of urls should be " + str(count)
                    error_list.append(msg)
        elif config.urls.end_url_distribution == EndUrlDistribution.NONE:
            for i, condition_links in enumerate(config.urls.end_url, start=1):
                if len(condition_links) != 1:
                    msg = "In distributionmode NONE only one url per condition is allowed"
                    error_list.append(msg)
        else:
            it = iter(config.urls.end_url)
            len_fst = len(next(it))
            if not all(len(l) == len_fst for l in it):
                msg = "In distributionmode RANDOM every condition should have the same number of links"
                error_list.append(msg)
        return error_list
