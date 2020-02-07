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
from enum import Enum


class SurveyType(Enum):
    """
    Enum for the different survey types.
    """
    SUBSCRIBE = 1
    DAILY = 2
    END = 3


class EndUrlDistribution(Enum):
    """
    Enum for the different end distribution strategies.
    """
    NONE = 0
    DAY = 1
    TIME = 2
    MIXED = 3
    RANDOM = 4

