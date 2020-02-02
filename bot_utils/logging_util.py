import logging
from typing import Tuple, List

from bot_utils.bot_enums import SurveyType


class LoggingUtil:
    """
    Util class for logging
    """

    @staticmethod
    def print_send_survey_command(logger: logging,
                                  chat_id: int,
                                  condition: int,
                                  survey_type: SurveyType) -> None:
        """
        Logs informations about sended surveys.

        :param logger: logger instance
        :param chat_id: chat id of the user
        :param condition: condition of the user
        :param survey_type: current survey type
        :return: None
        """
        logger.info("Send %s survey to %d with condition %d" % (survey_type.name, chat_id, condition))

    @staticmethod
    def print_send_broadcast(logger: logging,
                             subscriber_information: List[Tuple[int, int, int]],
                             survey_type: SurveyType) -> None:
        """
        Logs informations about sended surveys.

        :param logger: logger instance
        :param subscriber_information: subscriber information list
        :param survey_type: current survey type
        :return: None
        """
        for chat_id, condition, _ in subscriber_information:
            LoggingUtil.print_send_survey_command(logger, chat_id, condition, survey_type)
