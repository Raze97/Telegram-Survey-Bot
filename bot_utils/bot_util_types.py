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
from datetime import time
from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot_utils.bot_enums import SurveyType
from bot_utils.config_handler import ConfigHandler


class TimeSettings(object):
    """
    Timesettings object.
    """
    wakeup_time: time
    delay_minutes_after_wakeup: int
    survey_count: int
    delay_minutes_between_surveys: int

    def __init__(self, wakeup_time: time,
                 delay_minutes_after_wakeup: int,
                 survey_count: int,
                 delay_minutes_between_surveys: int) -> None:
        """
        Constructor.

        :param wakeup_time: The wakeup time
        :param delay_minutes_after_wakeup: The delay after wakeup until the first survey link
        :param survey_count: The number of surveys per day
        :param delay_minutes_between_surveys: The delay between the survey links
        """
        self.wakeup_time = wakeup_time
        self.delay_minutes_after_wakeup = delay_minutes_after_wakeup
        self.survey_count = survey_count
        self.delay_minutes_between_surveys = delay_minutes_between_surveys


class KeyboardBuilder:
    """
    Keyboard util class
    """

    @staticmethod
    def generate_link_markup(config_handler: ConfigHandler,
                             survey_type: SurveyType,
                             condition: int,
                             end_index: int = -1) -> InlineKeyboardMarkup:
        """
        Generate an InlineKeyboardMarkup with one button.
        The button references to the survey link, depending on the survey type and the user condition.

        :param config_handler: The config handler
        :param survey_type: The survey type
        :param condition: The condition of the user
        :param end_index: The end index for end surveys
        :return: The InlineKeyboardMarkup with one button
        """
        url: str = config_handler.get_url(survey_type, condition, end_index)

        button_list: List[InlineKeyboardButton] = [
            InlineKeyboardButton(text="Start", url=url)
        ]
        markup: InlineKeyboardMarkup = InlineKeyboardMarkup(KeyboardBuilder.build_menu(button_list, n_cols=1))
        return markup

    @staticmethod
    def build_menu(buttons: List[InlineKeyboardButton],
                   n_cols: int,
                   header_buttons=None,
                   footer_buttons=None) -> List[List[InlineKeyboardButton]]:
        """
        Builds a Buttonlist.

        :param buttons: the list of InlineKeyboardButton Objects
        :param n_cols: number of cols
        :param header_buttons: the header buttons list (default: {None})
        :param footer_buttons: the footer buttons list (default: {None})
        :return: the formatted buttonlist
        """
        menu: List[List[InlineKeyboardButton]] = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu
