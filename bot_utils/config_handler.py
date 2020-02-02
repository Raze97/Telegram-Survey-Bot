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

        :return:
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
