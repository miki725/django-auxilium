from __future__ import print_function, unicode_literals


try:
    from formtools.wizard.views import WizardView as _WizardView  # >=django1.8
except ImportError:
    from django.contrib.formtools.wizard.views import WizardView as _WizardView  # <django1.8


class WizardView(_WizardView):
    """
    Modified Django's ``WizardView`` which allows to specify ``form_list`` as
    class attribute.

    When using Django's ``WizardView``, the ``form_list`` must be specified
    when calling ``as_view()``::

        WizardView.as_view(form_list)

    This class allows to provide the ``form_list`` as class attribute::

        Wizard(WizardView):
            form_list = []

        Wizard.as_view()

    .. warning::
        This class requires `django-formtools <http://django-formtools.readthedocs.org/en/latest/>`_
        to be independently installed since this library does not install
        it as a dependency.
    """
    form_list = []

    @classmethod
    def get_initkwargs(cls, *args, **kwargs):
        """
        Custom ``get_initkwargs`` which adds ``form_list``
        to the super call when class defines any forms.
        """
        if cls.form_list:
            args = [cls.form_list] + list(args)
        return super(WizardView, cls).get_initkwargs(*args, **kwargs)
