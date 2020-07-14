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
import sys
from datetime import datetime, time
from typing import Callable, List, Tuple, Dict

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from past.builtins import raw_input
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.error import Unauthorized, InvalidToken, NetworkError, BadRequest
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageQueue, CallbackQueryHandler, MessageHandler, \
    Filters, ConversationHandler, Handler
from telegram.ext.callbackcontext import CallbackContext
from telegram.utils.request import Request

from bot_utils.bot_enums import SurveyType
from bot_utils.bot_util_types import KeyboardBuilder
from bot_utils.config_handler import ConfigHandler
from bot_utils.config_validator import ConfigValidationException
from bot_utils.db_handler import DbHandler
from bot_utils.logging_util import LoggingUtil
from bot_utils.message_queue_bot import MessageQueueBot
from bot_utils.schedule_util import ScheduleUtil
from bot_utils.time_util import TimeUtil

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)

TIMEZONE_STATE = 0
TIME_STATE = 1
CONDITION_STATE = 2
ER_YES = "ER_YES"
ER_NO = "ER_NO"
global_bot: MessageQueueBot
config_handler: ConfigHandler
schedule_util: ScheduleUtil
scheduler: BackgroundScheduler
db_handler: DbHandler
conversation_handler: ConversationHandler


def init_bot(message_queue: MessageQueue) -> MessageQueueBot:
    """
    Initializes the MessageQueueBot.

    :return: the MessageQueueBot instance
    """
    request: Request = Request(con_pool_size=200)
    return MessageQueueBot(token=config_handler.config.api_token, request=request, mqueue=message_queue)


def init_updater(bot: MessageQueueBot) -> Updater:
    """
    Initializes the Updater.

    :param bot: the MessageQueueBot instance
    :return: the Updater instance.
    """
    updater_instance: Updater = Updater(bot=bot, use_context=True)
    return updater_instance


def init_handlers(dispatcher: Dispatcher) -> None:
    """
    Initializes all handlers for the bot.
    The handlers for the subscribe, unsubscribe and start command will be initialized in every case.
    The handlers for the survey and help command and for the end-survey-reminder callback will be only initialized,
    if the associated fields in the config are set to 'True'.
    If time-calculation is enabled the subscribe handler is an entry point in a conversation handler.
    This conversation handler handles the wakeup time query.

    :param dispatcher: The Dispatcher instance from the Updater
    :return: None
    """
    global conversation_handler
    subscribe_handler = CommandHandler("subscribe", subscribe)
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("start", start))
    if config_handler.config.help.helpEnabled:
        dispatcher.add_handler(CommandHandler("help", send_help))
    if config_handler.config.surveyCommandEnabled:
        dispatcher.add_handler(CommandHandler("survey", send_survey))
    if config_handler.config.endSurveyReminderEnabled:
        dispatcher.add_handler(CallbackQueryHandler(handle_end_survey_reminder_callback))
    if config_handler.config.useTimeCalculation or \
            config_handler.config.participantsEnterCondition or \
            config_handler.config.useTimeZoneCalculation:
        states: Dict[int, List[Handler]] = {}
        if config_handler.config.useTimeZoneCalculation:
            regex_str = r"^\d{4}\.(0?[1-9]|1[012])\.(0?[1-9]|[12][0-9]|3[01])\-(0\d|1\d|2\d|\d):[0-5]\d$"
            regex_handler_timezone = MessageHandler(Filters.regex(regex_str), subscribe_timezone)
            states[TIMEZONE_STATE] = [regex_handler_timezone]
        if config_handler.config.participantsEnterCondition:
            regex_str = "^[0-%d]$" % (config_handler.get_condition_count() - 1)
            regex_handler_condition = MessageHandler(Filters.regex(regex_str), subscribe_condition)
            states[CONDITION_STATE] = [regex_handler_condition]
        if config_handler.config.useTimeCalculation:
            regex_handler_wakeup = MessageHandler(Filters.regex(r"^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$"),
                                                  subscribe_wakeup_time)
            states[TIME_STATE] = [regex_handler_wakeup]
        conversation_handler = ConversationHandler(
            entry_points=[subscribe_handler],
            states=states,
            fallbacks=[MessageHandler(Filters.all, subscribe_wakeup_time_fallback)]
        )
        dispatcher.add_handler(conversation_handler)
    else:
        dispatcher.add_handler(subscribe_handler)
    dispatcher.add_error_handler(error)


def schedule_notifications() -> None:
    """
    Schedules all time triggers with the APScheduler package.
    The time triggers are scheduled depending on the config settings.

    :return: None
    """
    if config_handler.config.linkDeletionSettings.start_DeleteLinkAtSubscriptionDeadline:
        schedule_util.schedule_delete_messages(delete_messages,
                                               config_handler.config.subscription_deadline,
                                               db_handler.query_and_delete_message_ids_by_type,
                                               SurveyType.SUBSCRIBE)

    schedule_util.schedule_surveys(send_notification_broadcast, SurveyType.DAILY)

    schedule_util.schedule_surveys(send_notification_broadcast, SurveyType.END)


def start_polling(updater: Updater, message_queue: MessageQueue) -> None:
    """
    Starts the bot.

    :return: None
    """
    try:
        updater.start_polling()
    except (Unauthorized, InvalidToken) as err:
        logging.error(err.message)
        logging.info("Check your API-Token in the config file")
        logging.info("Exiting...")
        raw_input()
        sys.exit(-1)
    except NetworkError:
        updater.start_polling()
    scheduler.start()
    updater.idle()
    scheduler.shutdown()
    message_queue.stop()


def start(update: Update, context: CallbackContext) -> None:
    """
    Handles the start command, which is automatically sent when a user starts a conversation with the bot.
    Sends the welcome message from the config file to the user.

    :param update: the Update of the start command
    :param context: the CallbackContext of the chat
    :return: None
    """
    chat_id = update.effective_chat.id
    context.bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.welcome)


def subscribe(update: Update, context: CallbackContext) -> int:
    """
    Handles the subscribe command. After a check if the user is in time to the subscription phase
    and is not already subscribed, the user is added to the database or will be asked about his wakeup time.


    :param update: the Update of the subscribe command
    :param context: the CallbackContext of the chat
    :return: the conversation state (int)
    """
    chat_id = update.effective_chat.id
    curr_date = datetime.now()
    if curr_date < config_handler.config.subscription_start_date:
        msg = context.bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.subscribe_early)
        schedule_util.schedule_delete_message(delete_message, 1, chat_id, msg.message_id)
    elif curr_date > config_handler.config.subscription_deadline:
        msg = context.bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.subscribe_late)
        schedule_util.schedule_delete_message(delete_message, 1, chat_id, msg.message_id)
    elif db_handler.is_already_subscribed(chat_id):
        msg = context.bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.subscribe_already)
        schedule_util.schedule_delete_message(delete_message, 1, chat_id, msg.message_id)
    else:
        condition = config_handler.get_condition()
        if not config_handler.config.participantsEnterCondition and \
                not config_handler.config.useTimeZoneCalculation and \
                schedule_util.add_subscriber(chat_id, condition):
            send_subscribe_message(context, chat_id, condition)
        else:
            if config_handler.config.useTimeZoneCalculation:
                text = config_handler.config.texts.subscribe_timezone + " (YYYY.MM.DD-HH:MM)"
                msg = context.bot.sendMessage(chat_id=chat_id,
                                              text=text)
                db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
                return TIMEZONE_STATE
            elif config_handler.config.useTimeCalculation:
                text = config_handler.config.texts.subscribe_wakeup_time + " (HH:MM)"
                msg = context.bot.sendMessage(chat_id=chat_id,
                                              text=text)
                db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
                return TIME_STATE
            else:
                text = config_handler.config.texts.subscribe_condition + \
                       " (0-%d)" % (config_handler.get_condition_count() - 1)
                msg = context.bot.sendMessage(chat_id=chat_id,
                                              text=text)
                db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
                return CONDITION_STATE


def error(update: Update, context: CallbackContext) -> None:
    """
    Log Errors caused by Updates.
    """
    logging.error("Update %s caused error %s" % (update, context.error))


def subscribe_timezone(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    offset = TimeUtil.get_time_offset(datetime.strptime(update.message.text, "%Y.%m.%d-%H:%M"))
    db_handler.insert_time_offset(chat_id, offset)
    condition = config_handler.get_condition()
    if not config_handler.config.participantsEnterCondition and \
            schedule_util.add_subscriber(chat_id, condition, send_notification_broadcast):
        send_subscribe_message(context, chat_id, condition)
        return ConversationHandler.END
    else:
        if config_handler.config.useTimeCalculation:
            text = config_handler.config.texts.subscribe_wakeup_time + " (HH:MM)"
            msg = context.bot.sendMessage(chat_id=chat_id,
                                          text=text)
            db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
            return TIME_STATE
        else:
            text = config_handler.config.texts.subscribe_condition + \
                   " (0-%d)" % (config_handler.get_condition_count() - 1)
            msg = context.bot.sendMessage(chat_id=chat_id,
                                          text=text)
            db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
            return CONDITION_STATE


def subscribe_wakeup_time(update: Update, context: CallbackContext) -> int:
    """
    Handles messages with the wakeup time of the user and add the user to the database.

    :param update: the Update of the subscribe command
    :param context: the CallbackContext of the chat
    :return: the conversation state (int)
    """
    chat_id = update.effective_chat.id
    if not config_handler.config.participantsEnterCondition:
        message_ids = db_handler.query_and_delete_message_ids([chat_id], SurveyType.SUBSCRIBE)
        for chat_id, message_id in message_ids:
            context.bot.deleteMessage(chat_id, message_id)
    wakeup_time: time = TimeUtil.get_time_from_str(update.message.text)
    condition: int = config_handler.get_condition()
    schedule_util.add_subscriber_time_calculated(chat_id, condition, wakeup_time, send_notification_broadcast)
    if config_handler.config.participantsEnterCondition:
        text = config_handler.config.texts.subscribe_condition + \
               " (0-%d)" % (config_handler.get_condition_count() - 1)
        msg = context.bot.sendMessage(chat_id=chat_id,
                                      text=text)
        db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
        return CONDITION_STATE
    else:
        send_subscribe_message(context, chat_id, condition)
        return ConversationHandler.END


def subscribe_condition(update: Update, context: CallbackContext) -> int:
    """
    Handles messages with the condition number of the user.

    :param update: the Update of the subscribe command
    :param context: the CallbackContext of the chat
    :return: the conversation state (int)
    """
    chat_id = update.effective_chat.id
    message_ids = db_handler.query_and_delete_message_ids([chat_id], SurveyType.SUBSCRIBE)
    for chat_id, message_id in message_ids:
        context.bot.deleteMessage(chat_id, message_id)
    condition = int(update.message.text)
    if config_handler.config.useTimeCalculation:
        db_handler.update_subscriber_condition(chat_id, condition)
    else:
        schedule_util.add_subscriber(chat_id, condition)
    send_subscribe_message(context, chat_id, condition)
    return ConversationHandler.END


def send_subscribe_message(context: CallbackContext, chat_id: int, condition: int) -> None:
    """
    Sends the start link with the subscribe message to a new subscriber.

    :param context: The callbackcontext
    :param chat_id: The chat id
    :param condition: The condition
    :return: None
    """
    mark_up = KeyboardBuilder.generate_link_markup(config_handler, SurveyType.SUBSCRIBE, condition)
    msg = context.bot.sendMessage(chat_id=chat_id,
                                  text=config_handler.config.texts.subscribe,
                                  reply_markup=mark_up)
    if config_handler.config.linkDeletionSettings.start_DeleteLinkTimer:
        schedule_util.schedule_delete_message(delete_message,
                                              config_handler.config.linkDeletionSettings
                                              .start_DeleteDelayMinutes,
                                              chat_id,
                                              msg.message_id)


def subscribe_wakeup_time_fallback(update: Update, context: CallbackContext) -> int:
    """
    Fallback handler. Will be called if the user not enters the wakeup time correctly.

    :param update: the Update of the subscribe command
    :param context: the CallbackContext of the chat
    :return: the conversation state (int)
    """
    chat_id = update.effective_chat.id
    db_handler.insert_message_id(chat_id, update.message.message_id, SurveyType.SUBSCRIBE)
    state_code = conversation_handler.conversations[(chat_id, chat_id)]
    if state_code == TIMEZONE_STATE:
        text = config_handler.config.texts.subscribe_timezone + " (YYYY.MM.DD-HH:MM)"
        msg = context.bot.sendMessage(chat_id=chat_id,
                                      text=text)
        db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
        return TIMEZONE_STATE
    elif state_code == TIME_STATE:
        text = config_handler.config.texts.subscribe_wakeup_time + " (HH:MM)"
        msg = context.bot.sendMessage(chat_id=chat_id,
                                      text=text)
        db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
        return TIME_STATE
    else:
        text = config_handler.config.texts.subscribe_condition + \
               " (0-%d)" % (config_handler.get_condition_count() - 1)
        msg = context.bot.sendMessage(chat_id=chat_id,
                                      text=text)
        db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.SUBSCRIBE)
        return CONDITION_STATE


def unsubscribe(update: Update, context: CallbackContext) -> None:
    """
    Handles the unsubscribe command and removes the chat id of the user from the sql database.
    Sends the unsubscribe message from the config file.

    :param update: the Update of the unsubscribe command
    :param context: the CallbackContext of the chat
    :return: None
    """
    chat_id = update.effective_chat.id
    db_handler.remove_subscriber(chat_id)
    context.bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.unsubscribe)


def send_help(update: Update, context: CallbackContext) -> None:
    """
    Sends a help message with all available commands to the user.

    :param update: the Update of the help command
    :param context: the CallbackContext of the chat
    :return: None
    """
    chat_id = update.effective_chat.id
    help_text = config_handler.config.help.help_text
    if config_handler.config.surveyCommandEnabled:
        help_text += config_handler.config.help.surveyCommandHelp
    context.bot.sendMessage(chat_id=chat_id, text=help_text)


def send_survey(update: Update, context: CallbackContext) -> None:
    """
    Handles the survey command.
    Sends the survey_reply message from the config file and the daily survey link to the user.

    :param update: the Update of the survey command
    :param context: the CallbackContext of the chat
    :return: None
    """
    chat_id = update.effective_chat.id
    condition = db_handler.get_condition(chat_id)
    markup: InlineKeyboardMarkup = KeyboardBuilder.generate_link_markup(config_handler, SurveyType.DAILY, condition)

    LoggingUtil.print_send_survey_command(logging, chat_id, condition, SurveyType.DAILY)

    msg: Message = context.bot.sendMessage(chat_id=chat_id,
                                           text=config_handler.config.texts.survey_reply,
                                           reply_markup=markup)
    db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.DAILY)

    if config_handler.config.linkDeletionSettings.daily_DeleteLinkTimer:
        schedule_util.schedule_delete_message(delete_message,
                                              config_handler.config.linkDeletionSettings.daily_DeleteDelayMinutes,
                                              chat_id,
                                              msg.message_id)


def send_notification_broadcast(survey_type: SurveyType, job_id: str, date_str: str) -> None:
    """
    Sends a survey link and the reminder message from the config file to the users.

    :param survey_type: The type of the survey
    :param job_id: The APScheduler job id
    :param date_str: The execution date as string to address the users
    :return: None
    """
    remove_job_from_scheduler(job_id)

    subscriber_information: List[Tuple[int, int, int]] = db_handler.query_subscribers_by_date_type(date_str,
                                                                                                   survey_type.name)
    if config_handler.config.linkDeletionSettings.daily_DeleteLinkAtNewLink or \
            config_handler.config.linkDeletionSettings.end_DeleteLinkAtNewLink:
        delete_messages(db_handler.query_and_delete_message_ids,
                        [x[0] for x in subscriber_information],
                        survey_type)

    msg_text: str = config_handler.get_message(survey_type)

    LoggingUtil.print_send_broadcast(logging, subscriber_information, survey_type)

    for chat_id, condition, end_index in subscriber_information:
        markup: InlineKeyboardMarkup = KeyboardBuilder.generate_link_markup(config_handler,
                                                                            survey_type,
                                                                            condition,
                                                                            end_index)
        try:
            msg = global_bot.sendMessage(chat_id=chat_id, text=msg_text, reply_markup=markup)
            db_handler.insert_message_id(chat_id, msg.message_id, survey_type)
        except Unauthorized as err:
            logging.error("Can't send survey to %d because: %s" % (chat_id, err.message))

    chat_id_list = [chat_id for chat_id, _, _ in subscriber_information]

    if survey_type == SurveyType.END and config_handler.config.endSurveyReminderEnabled:
        schedule_util.schedule_end_survey_reminder(send_end_survey_reminder,
                                                   subscriber_information)
    if survey_type == SurveyType.DAILY and config_handler.config.linkDeletionSettings.daily_DeleteLinkTimer:
        schedule_util.schedule_delete_message(delete_messages,
                                              config_handler.config.linkDeletionSettings.daily_DeleteDelayMinutes,
                                              db_handler.query_and_delete_message_ids,
                                              chat_id_list,
                                              survey_type)
    elif survey_type == SurveyType.END and config_handler.config.linkDeletionSettings.end_DeleteLinkTimer:
        schedule_util.schedule_delete_message(delete_messages,
                                              config_handler.config.linkDeletionSettings.end_DeleteDelayMinutes,
                                              db_handler.query_and_delete_message_ids,
                                              chat_id_list,
                                              survey_type)


def remove_job_from_scheduler(job_id: str) -> None:
    """
    Tries to remove a job with a specific id from the scheduler.
    The job can only be removed, if the jitter executes the job earlier than the time in the times array.
    Then the job can be rescheduled for a time after the time in times array,
    which will be an unwanted duplicate execution.

    :param job_id: The job id of the job
    :return: None
    """
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        logging.info("Job with id " + job_id + " not rescheduled")


def send_end_survey_reminder(chat_id_list: List[int], date_str: str) -> None:
    """
    Sends the end-survey-reminder to the users
    The end-survey-reminder contains two buttons, yes and no, and the endSurveyReminder message from the config.

    :return: None
    """
    callback_yes = ER_YES + "+" + date_str
    callback_no = ER_NO + "+" + date_str

    button_list = [
        InlineKeyboardButton(text=config_handler.config.texts.endSurveyReminderYes, callback_data=callback_yes),
        InlineKeyboardButton(text=config_handler.config.texts.endSurveyReminderNo, callback_data=callback_no),
    ]
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(KeyboardBuilder.build_menu(button_list, n_cols=1))

    for chat_id in chat_id_list:
        global_bot.sendMessage(chat_id=chat_id, text=config_handler.config.texts.endSurveyReminder, reply_markup=markup)


def handle_end_survey_reminder_callback(update: Update, context: CallbackContext) -> None:
    """
    Handles the end survey reminder callback, which is sent when a user clicks on a button of
    the end survey reminder message. In every case the end survey reminder message will be deleted.
    If the user clicks 'no' the end survey link will be sent to this user.

    :param update: the Update of the end survey reminder callback
    :param context: the CallbackContext of the chat
    :return: None
    """
    chat_id = update.effective_chat.id
    callback_code = update.callback_query.data.split("+")
    message_id = update.callback_query.message.message_id

    context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
    if callback_code[0] == ER_NO:
        condition, end_index = db_handler.get_condition_and_end_index(chat_id, callback_code[1])
        mark_up = KeyboardBuilder.generate_link_markup(config_handler, SurveyType.END, condition, end_index)
        msg = context.bot.sendMessage(chat_id=chat_id,
                                      text=config_handler.config.texts.endSurveyReminder,
                                      reply_markup=mark_up)
        if config_handler.config.linkDeletionSettings.end_DeleteLinkAtNewLink:
            db_handler.insert_message_id(chat_id, msg.message_id, SurveyType.END)
        if config_handler.config.linkDeletionSettings.end_DeleteLinkTimer:
            schedule_util.schedule_delete_message(delete_messages,
                                                  config_handler.config.linkDeletionSettings.end_DeleteDelayMinutes,
                                                  db_handler.query_and_delete_message_ids,
                                                  [chat_id],
                                                  SurveyType.END)


def delete_messages(query_function: Callable, *func_args) -> None:
    """
    Delete all link messages. The chat ids and the message ids will be queried from the database,
    depending on the query_function.

    :param query_function: The DbHandler function to query the ids
    :param func_args: The arguments for the query_function
    :return: None
    """
    id_list: List[tuple] = query_function(*func_args)

    for chat_id, message_id in id_list:
        try:
            global_bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        except BadRequest as err:
            logging.error("Can't delete message %d in chat %d because: %s" % (message_id, chat_id, err.message))


def delete_message(chat_id: int, message_id: int) -> None:
    """
    Deletes on message to a given chat- and message id.

    :param chat_id: The chat id
    :param message_id: The message id
    :return: None
    """
    try:
        global_bot.deleteMessage(chat_id=chat_id, message_id=message_id)
    except BadRequest as err:
        logging.error("Can't delete message %d in chat %d because: %s" % (message_id, chat_id, err.message))


def main() -> None:
    """
    Main method. Initializes all required variables and starts the bot.

    :return: None
    """
    global config_handler, global_bot, schedule_util, db_handler, scheduler
    logging.info("Load Config...")
    try:
        config_handler = ConfigHandler()
    except ConfigValidationException as err:
        for message in err.message_list:
            logging.error(message)
        logging.info("Exiting... press Enter")
        raw_input()
        sys.exit(-1)
    except (ValueError, TypeError, KeyError) as err:
        logging.error(str(type(err).__name__) + ": " + str(err))
        logging.info("Exiting...")
        raw_input()
        sys.exit(-1)
    logging.info("Init...")
    executors = {
        'default': ThreadPoolExecutor(200)
    }
    scheduler = BackgroundScheduler(executors=executors)
    message_queue: MessageQueue = MessageQueue(all_burst_limit=20, all_time_limit_ms=1000)
    try:
        global_bot = init_bot(message_queue)
    except InvalidToken as err:
        logging.error(err.message)
        logging.info("Check your API-Token in the config file")
        logging.info("Exiting...")
        raw_input()
        sys.exit(-1)
    updater: Updater = init_updater(global_bot)
    db_handler = DbHandler()
    schedule_util = ScheduleUtil(scheduler, config_handler.config, db_handler)
    init_handlers(updater.dispatcher)
    schedule_notifications()
    logging.info("Start...")
    start_polling(updater, message_queue)


if __name__ == '__main__':
    main()
