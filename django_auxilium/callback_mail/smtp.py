from __future__ import print_function, unicode_literals

from django.core.mail.backends.smtp import EmailBackend

from .base import BaseCallbackEmailBackendMixin


class CallbackEmailBackend(BaseCallbackEmailBackendMixin, EmailBackend):
    """
    Custom SMPT email backend which sends signals on progress events
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
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                for message in email_messages:
                    self.failed(message, 'Could not establish connection')
                return
            num_sent = 0
            for message in email_messages:
                self.sending(message)
                sent = self._send(message)
                if sent:
                    self.sent(message)
                    num_sent += 1
                else:
                    self.failed(message, 'Could not send email over SMTP')
            if new_conn_created:
                self.close()
        return num_sent
