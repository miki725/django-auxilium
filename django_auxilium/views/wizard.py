from __future__ import unicode_literals, print_function
from django.contrib.formtools.wizard.views import WizardView


class WizardView(WizardView):
    """
    Modified Django's ``WizardView`` which allows to specify ``form_list`` as
    class attribute.

    When using Django's ``WizardView``, the ``form_list`` must be specified when calling
    ``as_view()``::

        WizardView.as_view(form_list)

    This class allows to provide the form_list as class attribute::

        Wizard(WizardView):
            form_list = ()

        Wizard.as_view()
    """
    form_list = ()

    @classmethod
    def get_initkwargs(cls, *args, **kwargs):
        if cls.form_list:
            args = [cls.form_list] + list(args)
        return super(WizardView, cls).get_initkwargs(*args, **kwargs)
