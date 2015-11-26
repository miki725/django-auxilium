"""
This package provides provides custom email backends
which use Django signals framework to send signals
when various mail sending progress events occur.

You can refer to :py:mod:`.signals` for a full
list of supported signals.

In order to enable this functionality, you need to
change your Django email backend::

    EMAIL_BACKEND = 'django_auxilium.callback_mail.filebased.EmailBackend'

Examples
--------

::

    from django.dispatch import receiver
    from django_auxilium.callback_mail.signals import sent_mail

    @receiver(sent_mail)
    def my_callback(sender, message):
        print("Message sent!")
"""
