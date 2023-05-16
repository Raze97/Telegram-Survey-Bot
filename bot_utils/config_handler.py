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
import json
from pathlib import Path
from random import randint

from bot_utils.bot_enums import SurveyType
from bot_utils.config import Config
from bot_utils.config_validator import ConfigValidator

jsonFile = Path("config/") / "config.json"


class ConfigHandler(object):
    """
    Class to parse and handle the config file.
    """
    config: Config

    def __init__(self) -> None:
        """
        Constructor. Load the config.json file.
        """
        with open(jsonFile, encoding='utf-8') as file:
            data = json.load(file)
            self.config = Config(**data)
            ConfigValidator.validate_config(self.config)

    def get_condition_count(self) -> int:
        """
        Returns the count of conditions, by counting the numbers of start urls in the config.

        :return: count of conditions (int)
        """
        return len(self.config.urls.start_url)

    def get_condition(self) -> int:
        """
        Returns a random condition, depending on the number of links.

        :return: random choosed condition (int)
        """
        return randint(0, len(self.config.urls.start_url) - 1)

    def get_url(self, survey_type: SurveyType, condition: int, end_distribution: int) -> str:
        """
        Returns the link url depending on the given survey type, condition and end_distribution_index for end surveys.

        :param survey_type: The survey type
        :param condition: The condition of the user
        :param end_distribution: The end url index
        :return: The survey link (str)
        """
        if survey_type == SurveyType.SUBSCRIBE:
            return self.config.urls.start_url[condition]
        elif survey_type == SurveyType.DAILY:
            return self.config.urls.daily_url[condition]
        else:
            return self.config.urls.end_url[condition][end_distribution]

    def get_message(self, survey_type: SurveyType) -> str:
        """
        Returns the message depending on the given survey type.

        :param survey_type: The survey type
        :return: The message text (str)
        """
        if survey_type == SurveyType.DAILY:
            return self.config.texts.daily_reminder
        if survey_type == SurveyType.END:
            return self.config.texts.end_reminder
