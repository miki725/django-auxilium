from __future__ import unicode_literals

from .signals import failed_mail, sending_mail, sent_mail


class BaseCallbackEmailBackendMixin(object):
    """
    Base class for implementing callback email backends.

    "Callback" is used in a sense that appropriate signals
    are sent while sending message.

    :Sending: :py:data:`.signals.sending_mail` signal is sent when
              message is in progress of being sent
    :Sent:    :py:data:`.signals.sent_mail` signal is sent when
              message was successfully sent
    :Failed:  :py:data:`.signals.failed_mail` signal is sent when
              message sending failed
    """

    def sending(self, message):
        """
        Hook which sends signal when message is being sent
        """
        sending_mail.send(sender=self.__class__, message=message)

    def sent(self, message):
        """
        Hook which sends signal when message was successfully sent
        """
        sent_mail.send(sender=self.__class__, message=message)

    def failed(self, message, reason=None):
        """
        Hook which sends signal when sending message failed
        """
        failed_mail.send(
            sender=self.__class__,
            message=message,
            reason=reason
        )
