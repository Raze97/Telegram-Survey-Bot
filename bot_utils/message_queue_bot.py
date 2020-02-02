import telegram.bot
from telegram.ext import messagequeue as mq, MessageQueue


class MessageQueueBot(telegram.bot.Bot):
    """
    A subclass of Bot which delegates send method handling to MessageQueue.
    """
    _is_messages_queued_default: bool
    _msg_queue: MessageQueue

    def __init__(self, *args, is_queued_def=True, mqueue: MessageQueue = None, **kwargs) -> None:
        """
        Constructor.

        :param is_queued_def: if messages queued on default (default: {True})
        :param mqueue: the MessageQueue Object (default: {None})
        """
        super(MessageQueueBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        """
        Stops the messagequeue.
        """
        try:
            self._msg_queue.stop()
        except Exception:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """
        Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments
        """
        return super(MessageQueueBot, self).send_message(*args, **kwargs)
