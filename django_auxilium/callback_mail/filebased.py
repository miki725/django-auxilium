from __future__ import print_function, unicode_literals

from django.core.mail.backends.filebased import EmailBackend

from .base import BaseCallbackEmailBackendMixin


class CallbackEmailBackend(BaseCallbackEmailBackendMixin, EmailBackend):
    """
    Custom file-based email backend which sends signals on progress events
    of sending messages.
    """

    def send_messages(self, email_messages):
        """
        Custom implementation of sending messages which also
        calls mail signals.

        Unfortunately vanilla Django implementation does not
        provide enough hooks for when messages are sent
        hence this method needs to duplicate the whole method.
        """
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self.sending(message)
                    self.write_message(message)
                    self.sent(message)
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                for message in email_messages:
                    self.failed(message, 'Could not write emails to file')
                if not self.fail_silently:
                    raise
        return msg_count
