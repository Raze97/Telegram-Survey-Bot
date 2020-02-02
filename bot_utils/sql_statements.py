
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
