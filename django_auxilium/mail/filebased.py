from django.core.mail.backends.filebased import EmailBackend


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
            try:
                stream_created = self.open()
                for message in email_messages:
                    self.sending(message)
                    self.stream.write('%s\n' % message.message().as_string())
                    self.stream.write('-' * 79)
                    self.stream.write('\n')
                    self.stream.flush()  # flush after each message
                    self.sent(message)
                if stream_created:
                    self.close()
            except:
                for message in email_messages:
                    self.failed(message,
                                'Could not write emails to file')
                if not self.fail_silently:
                    raise
        return len(email_messages)
