from django.core.mail.backends.smtp import EmailBackend


class CallbackEmailBackend(EmailBackend):
    def sending(self, message):
        pass

    def sent(self, message):
        pass

    def failed(self, message, error_message=None):
        pass

    def send_messages(self, email_messages):
        if not email_messages:
            return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                for message in email_messages:
                    self.failed(message,
                                'Could not establish connection')
                return
            num_sent = 0
            for message in email_messages:
                self.sending(message)
                num_sent = self._send(message)
                if num_sent:
                    num_sent += 1
                    self.sent(message)
                else:
                    self.failed(message,
                                'Could not send email over SMTP')
            if new_conn_created:
                self.close()
        return num_sent
