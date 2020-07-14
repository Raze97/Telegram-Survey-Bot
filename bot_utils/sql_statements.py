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
CREATE_TABLE_SUBSCRIBER = """ CREATE TABLE IF NOT EXISTS subscribers (
                                chat_id integer, 
                                date text,
                                type text,
                                condition integer,
                                end_index integer 
                        ); """

CREATE_TABLE_MESSAGES = """ CREATE TABLE IF NOT EXISTS messages (
                                chat_id integer, 
                                message_id integer,
                                type text 
                        ); """

CREATE_TABLE_OFFSETS = """ CREATE TABLE IF NOT EXISTS offsets (
                                chat_id integer, 
                                offset integer
                        ); """

INSERT_SUBSCRIBER = "INSERT INTO subscribers VALUES(?, ?, ?, ?, ?)"
UPDATE_SUBSCRIBER = "UPDATE subscribers SET condition=? WHERE chat_id=?"
SELECT_SUBSCRIBER_ALL = "SELECT * FROM subscribers"
SELECT_SUBSCRIBER_DATE_TYPE = "SELECT chat_id, condition, end_index FROM subscribers WHERE date=? AND type=?"
SELECT_SUBSCRIBER_ID_DATE = "SELECT condition, end_index FROM subscribers WHERE chat_id=? AND date=?"
SELECT_SUBSCRIBER_CHAT_ID = "SELECT * FROM subscribers WHERE chat_id=?"
DELETE_SUBSCRIBER = "DELETE FROM subscribers WHERE chat_id=?"

INSERT_MESSAGE = "INSERT INTO messages VALUES(?, ?, ?)"
SELECT_MESSAGE = "SELECT * FROM messages WHERE chat_id=? AND message_id=? AND type=?"
SELECT_MESSAGE_TYPE = "SELECT chat_id, message_id FROM messages WHERE type=?"
SELECT_MESSAGE_ID = "SELECT chat_id, message_id FROM messages WHERE chat_id=? AND type=?"
DELETE_MESSAGE = "DELETE FROM messages WHERE chat_id=?"
DELETE_MESSAGE_TYPE = "DELETE FROM messages WHERE type=?"
DELETE_MESSAGE_ID = "DELETE FROM messages WHERE chat_id=? AND type=?"

INSERT_OFFSET = "INSERT INTO offsets VALUES(?, ?)"
SELECT_OFFSET = "SELECT offset FROM offsets WHERE chat_id=?"
DELETE_OFFSET = "DELETE FROM offsets WHERE chat_id=?"
