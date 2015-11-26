from __future__ import absolute_import, print_function, unicode_literals

from django import forms

from django_auxilium.views.wizard import WizardView


class TestForm(forms.Form):
    pass


class TestWizardView(WizardView):
    form_list = [TestForm]


def test_wizard_view():
    assert TestWizardView.get_initkwargs()['form_list'] == {
        '0': TestForm,
    }
