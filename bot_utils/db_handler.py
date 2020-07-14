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
import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import Error, Connection
from typing import List, Tuple, Any

from bot_utils.bot_enums import SurveyType
from bot_utils.sql_statements import CREATE_TABLE_MESSAGES, CREATE_TABLE_SUBSCRIBER, CREATE_TABLE_OFFSETS, \
    INSERT_MESSAGE, INSERT_SUBSCRIBER, SELECT_SUBSCRIBER_DATE_TYPE, SELECT_SUBSCRIBER_CHAT_ID, DELETE_MESSAGE, \
    DELETE_SUBSCRIBER, SELECT_MESSAGE_ID, SELECT_MESSAGE_TYPE, DELETE_MESSAGE_ID, DELETE_MESSAGE_TYPE, \
    SELECT_SUBSCRIBER_ID_DATE, UPDATE_SUBSCRIBER, INSERT_OFFSET, SELECT_OFFSET, DELETE_OFFSET

dbFile = Path("db/") / "userIdDb.db"


class DbHandler:
    """
    A class for all interactions to the SQLite Database,
    which stores the chat-ids, message-ids and other information to adress the users.
    """

    def __init__(self) -> None:
        """
        Creates a connection to the SQLite Database-file and
        create, if not exist, all needed tables.
        """
        conn = self.create_connection()
        if conn is not None:
            self.create_table(conn, CREATE_TABLE_SUBSCRIBER)
            self.create_table(conn, CREATE_TABLE_MESSAGES)
            self.create_table(conn, CREATE_TABLE_OFFSETS)
            conn.close()

    @staticmethod
    def create_connection() -> Connection:
        """
        Creates a connection to the SQLite Database-file.

        :return: the Connection instance
        """
        conn = None
        try:
            conn = sqlite3.connect(dbFile)
        except Error as e:
            print(e)

        return conn

    @staticmethod
    def create_table(conn: Connection, command: str) -> None:
        """
        Creates a new table if it not already exists.

        :param conn: The database Connection instance
        :param command: The SQL-command string
        :return: None
        """
        try:
            c = conn.cursor()
            c.execute(command)
        except Error as e:
            print(e)

    def insert_end_reminder_entries_from_list(self,
                                              survey_type: SurveyType,
                                              subscriber_information: List[Tuple[int, int, int]],
                                              date_str: str) -> None:
        """
        Inserts entries for end survey reminder.

        :param survey_type: The survey type
        :param subscriber_information:
        :param date_str:
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        for chat_id, condition, end_index in subscriber_information:
            cursor.execute(INSERT_SUBSCRIBER, (chat_id, date_str, survey_type.name, condition, end_index))
        connection.commit()
        connection.close()

    def insert_new_subscriber_entries(self, chat_id: int,
                                      date_list: List[datetime],
                                      survey_type: SurveyType,
                                      condition: int,
                                      end_distribution_list: List[int] = None) -> None:
        """
        Inserts subscriber entries.

        :param chat_id: The chat id of the new subscriber
        :param date_list: The Datetime list
        :param survey_type: The survey type
        :param condition: The condition number
        :param end_distribution_list: The end distribution list (optional)
        :return: None
        """
        end_distribution: int = -1
        connection = self.create_connection()
        cursor = connection.cursor()
        for i, date in enumerate(date_list):
            if survey_type == SurveyType.END and end_distribution_list is not None:
                end_distribution = end_distribution_list[i]
            date_str = date.strftime("%Y-%m-%d-%H:%M")
            cursor.execute(INSERT_SUBSCRIBER, (chat_id, date_str, survey_type.name, condition, end_distribution))
        connection.commit()
        connection.close()

    def update_subscriber_condition(self, chat_id: int, condition: int) -> None:
        """
        Updates the condition number of one subscriber.

        :param chat_id: The chat id of the subscriber
        :param condition: The new entered condition of the subscriber
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(UPDATE_SUBSCRIBER, (condition, chat_id))
        connection.commit()
        connection.close()

    def is_already_subscribed(self, chat_id: int) -> bool:
        """
        Returns if the given chat id is already subscribed.

        :param chat_id: The chat id to check
        :return: if the chat id is already subscribed (bool)
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_SUBSCRIBER_CHAT_ID, (chat_id,))

        rows = cursor.fetchall()

        connection.close()

        return bool(rows)

    def query_subscribers_by_date_type(self, date_str: str, type_str: str) -> List[Tuple[int, int, int]]:
        """
        Query all subscribers to a specific date string and survey type.

        :param date_str: The date string
        :param type_str: The type string
        :return: List with Triples (chat id, condition, end index)
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_SUBSCRIBER_DATE_TYPE, (date_str, type_str))

        rows = cursor.fetchall()

        connection.close()
        return rows

    def get_condition(self, chat_id: int) -> int:
        """
        Returns the condition of a given chat id.

        :param chat_id: The chat id
        :return: The condition
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_SUBSCRIBER_CHAT_ID, (chat_id,))

        rows = cursor.fetchall()

        connection.close()

        return rows[0][3]

    def get_condition_and_end_index(self, chat_id: int, date_str: str) -> Tuple[int, int]:
        """
        Returns the condition and the end index of a given chat id and date string.

        :param chat_id: The chat id
        :param date_str: The date string
        :return: Tuple (condition, end index)
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_SUBSCRIBER_ID_DATE, (chat_id, date_str))

        rows = cursor.fetchall()

        connection.close()

        return rows[0]

    def remove_subscriber(self, chat_id: int) -> None:
        """
        Removes a subscriber from the database.

        :param chat_id: The chat id
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(DELETE_MESSAGE, (chat_id,))
        cursor.execute(DELETE_SUBSCRIBER, (chat_id,))
        connection.commit()
        connection.close()

    def insert_message_id(self, chat_id: int, message_id: int, survey_type: SurveyType) -> None:
        """
        Inserts a message id with the survey type.

        :param chat_id: The chat id
        :param message_id: The message id
        :param survey_type: The survey type
        :return: None
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(INSERT_MESSAGE, (chat_id, message_id, survey_type.name))
        connection.commit()
        connection.close()

    def query_and_delete_message_ids(self, chat_ids: List[int], survey_type: SurveyType) -> List[Tuple[int, int]]:
        """
        Query all message ids to a list of chat ids and a specific survey type.

        :param chat_ids: The chat id list
        :param survey_type: The survey type
        :return: List of tuples (chat id, message id)
        """
        chat_message_ids: List[tuple] = []

        connection = self.create_connection()
        cursor = connection.cursor()
        for chat_id in chat_ids:
            cursor.execute(SELECT_MESSAGE_ID, (chat_id, survey_type.name))
            rows = cursor.fetchall()
            chat_message_ids.extend(rows)
            cursor.execute(DELETE_MESSAGE_ID, (chat_id, survey_type.name))

        connection.commit()
        connection.close()
        return chat_message_ids

    def query_and_delete_message_ids_by_type(self, survey_type: SurveyType) -> List[Tuple[int, int]]:
        """
        Query all message ids to a specific survey type.

        :param survey_type: The survey type
        :return: List of tuples (chat id, message id)
        """
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_MESSAGE_TYPE, (survey_type.name,))
        rows = cursor.fetchall()
        cursor.execute(DELETE_MESSAGE_TYPE, (survey_type.name,))
        connection.commit()
        connection.close()
        return rows

    def insert_time_offset(self, chat_id: int, offset: int) -> None:
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(INSERT_OFFSET, (chat_id, offset))
        connection.commit()
        connection.close()

    def get_time_offset(self, chat_id: int) -> int:
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(SELECT_OFFSET, (chat_id,))

        rows = cursor.fetchall()

        connection.close()

        if not rows or not rows[0]:
            return 0
        else:
            return rows[0][0]
