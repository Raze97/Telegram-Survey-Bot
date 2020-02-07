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
