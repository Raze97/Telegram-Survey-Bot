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
SUBSCRIPTION_REJECTED = "Subscription rejected for {} because: {}"
SUBSCRIPTION_EARLY = "Early"
SUBSCRIPTION_LATE = "Late"
SUBSCRIPTION_ALREADY_SUBSCRIBED = "Already subscribed"
SUBSCRIPTION_HANDLE = "Handle Subscription of: {}"
SUBSCRIPTION_ASK = "Subscription ask {}: {}"
SUBSCRIPTION_TIMEZONE = "Timezone"
SUBSCRIPTION_TIME_CALC = "Wakeup time"
SUBSCRIPTION_CONDITION = "Condition"
SUBSCRIPTION_TIMEZONE_DELTA = "Got timezonedelta for {}: {}"
SUBSCRIPTION_WAKEUP_TIME = "Got wakeup time for {}: {}"
SUBSCRIPTION_GOT_CONDITION = "Got condition for {}: {}"
SUBSCRIPTION_FINISHED = "Send subscribe survey to {}"
UNSUBSCRIBE = "Got unsubscribe command from {}"
SEND_SURVEY = "Send survey of type {} to {}"
SU_ADD_JOB = "Add job with id: {}"
DB_UPDATE_CONDITION = "Update condition for {}: {}"
DB_INSERT_SUBSCRIBER_ENTRY = "Insert subscriber entries:"
DB_INSERT_SUBSCRIBER_ENTRY_DATA = "chat_id: {}, date_str: {}, survey_type: {}, condition: {}, end_distribution: {}"
EMERGENCY_DATES_FOUND = "\n" \
                        "--------------!!!!!!!     WARNING!     !!!!!!!--------------\n\n" \
                        "Found {} future survey dates. Do you want to reschedule them?\n\n" \
                        "--------------!!!!!!! PRESS [Y]es/[N]o !!!!!!!--------------"
EMERGENCY_DATES_WARN = "\n" \
                       "--------------!!!!!!!     WARNING!     !!!!!!!--------------\n\n" \
                       "Should be the date entries be removed from the Database?\n" \
                       "If not, all previous subscribed users\n" \
                       "can not subscribe to the Bot anymore!\n\n" \
                       "--------------!!!!!!! PRESS [Y]es/[N]o !!!!!!!--------------"
EMERGENCY_DATES_RESCHEDULE = "Reschedule {} survey dates:"
EMERGENCY_DATES_IGNORE = "Ignore {} survey dates"
EMERGENCY_DATES_IGNORE_DELETE = "Ignore and delete {} survey dates"
