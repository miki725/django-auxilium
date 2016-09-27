from __future__ import absolute_import, print_function, unicode_literals

from django import forms

from django_auxilium.views.wizard import WizardView


class _TestForm(forms.Form):
    pass


class _TestWizardView(WizardView):
    form_list = [_TestForm]


def test_wizard_view():
    assert _TestWizardView.get_initkwargs()['form_list'] == {
        '0': _TestForm,
    }
