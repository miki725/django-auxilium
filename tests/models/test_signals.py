from __future__ import print_function, unicode_literals

import mock
import pytest
from dirtyfields import DirtyFieldsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.test import TestCase

from django_auxilium.models import (
    AutoSignals,
    FieldSpec,
    FileFieldAutoChangeDelete,
    FileFieldAutoDelete,
)


class TestFileFieldAutoDelete(object):
    def setup_method(self, method):
        self.decorator = FileFieldAutoDelete()

    def get_model(self):
        class Model(models.Model):
            file_field = models.FileField(upload_to='foo')
            foo_field = models.CharField(max_length=32)

            class Meta(object):
                app_label = 'foo'

        return Model

    def get_empty_model(self):
        class ModelEmpty(models.Model):
            class Meta(object):
                app_label = 'foo'

        return ModelEmpty

    def test_init(self):
        decorator = FileFieldAutoDelete()

        assert decorator.field_names == '*'
        assert decorator.signal is models.signals.post_delete
        assert decorator.signal_name_pattern == 'post_delete_{model.__name__}_delete_{field}'

    @mock.patch.object(FileFieldAutoDelete, 'connect_signal_function')
    @mock.patch.object(FileFieldAutoDelete, 'validate_fields')
    @mock.patch.object(FileFieldAutoDelete, 'get_field_names')
    @mock.patch.object(FileFieldAutoDelete, 'get_fields')
    @mock.patch.object(FileFieldAutoDelete, 'validate_model')
    def test_get_wrapped_object(self, mock_validate_model,
                                mock_get_fields, mock_get_field_names,
                                mock_validate_fields,
                                mock_connect_signal_function):
        self.decorator.to_wrap = mock.sentinel.model

        # sanity assert
        assert self.decorator.field_names == '*'
        assert self.decorator.get_wrapped_object() is mock.sentinel.model
        assert self.decorator.field_names == mock_get_field_names.return_value
        assert self.decorator.fields == mock_get_fields.return_value

        mock_validate_model.assert_called_once_with()
        mock_get_field_names.assert_called_once_with()
        mock_get_fields.assert_called_once_with()
        mock_validate_fields.assert_called_once_with()
        mock_connect_signal_function.assert_called_once_with()

    def test_validate_model_not_class(self):
        self.decorator.to_wrap = None

        with pytest.raises(TypeError):
            self.decorator.validate_model()

    def test_validate_model_not_model(self):
        self.decorator.to_wrap = int

        with pytest.raises(TypeError):
            self.decorator.validate_model()

    def test_validate_model(self):
        self.decorator.to_wrap = self.get_empty_model()

        assert self.decorator.validate_model() is None

    def test_get_field_names_single_field(self):
        self.decorator.field_names = 'foo'

        assert self.decorator.get_field_names() == ['foo']

    def test_get_field_names_single_multiple_fields(self):
        self.decorator.field_names = ['foo', 'bar']

        assert self.decorator.get_field_names() == ['foo', 'bar']

    def test_get_field_names_single_wildcard(self):
        self.decorator.field_names = '*'
        self.decorator.to_wrap = self.get_model()

        assert self.decorator.get_field_names() == ['file_field']

    @mock.patch.object(FileFieldAutoDelete, 'validate_field')
    def test_validate_fields(self, mock_validate_field):
        self.decorator.field_names = ['foo']

        assert self.decorator.validate_fields() is None

        mock_validate_field.assert_called_once_with('foo')

    def test_validate_field_not_present(self):
        self.decorator.to_wrap = self.get_model()

        with pytest.raises(AttributeError):
            self.decorator.validate_field('foo')

    def test_validate_field_not_filefield(self):
        self.decorator.to_wrap = self.get_model()

        with pytest.raises(TypeError):
            self.decorator.validate_field('foo_field')

    def test_validate_field(self):
        self.decorator.to_wrap = self.get_model()

        assert self.decorator.validate_field('file_field') is None

    def test_get_signal_name_single(self):
        self.decorator.to_wrap = self.get_model()
        self.decorator.fields = [FieldSpec('foo', None)]

        name = self.decorator.get_signal_name()
        assert name == 'post_delete_Model_delete_foo'

    def test_get_signal_name_multiple(self):
        self.decorator.to_wrap = self.get_model()
        self.decorator.fields = [FieldSpec('foo', None), FieldSpec('bar', None)]

        name = self.decorator.get_signal_name()
        assert name == 'post_delete_Model_delete_foo_bar'

    def test_get_signal_function_no_file(self):
        model = self.get_model()
        self.decorator.to_wrap = model
        self.decorator.fields = [FieldSpec('file_field', None)]

        signal = self.decorator.get_signal_function()

        assert callable(signal)

        f = mock.MagicMock(spec=ContentFile)
        instance = model(file_field=f)

        assert signal(model, instance) is None
        assert not f.mock_calls

    def test_get_signal_function_with_file(self):
        model = self.get_model()
        self.decorator.to_wrap = model
        self.decorator.fields = [FieldSpec('file_field', None)]

        signal = self.decorator.get_signal_function()

        assert callable(signal)

        f = mock.MagicMock()
        instance = model(file_field=f)

        assert signal(model, instance) is None
        f.delete.assert_called_once_with(save=False)

    @mock.patch.object(FileFieldAutoDelete, 'get_signal_function')
    def test_connect_signal_function(self, mock_get_signal_function):
        self.decorator.signal = signal = mock.MagicMock()
        self.decorator.fields = [FieldSpec('foo', None)]
        self.decorator.to_wrap = model = self.get_model()

        assert self.decorator.connect_signal_function() is None
        signal.connect.assert_called_once_with(
            mock_get_signal_function.return_value,
            sender=model,
            weak=False,
            dispatch_uid='post_delete_Model_delete_foo'
        )


class TestFileFieldAutoChangeDelete(TestCase):
    def setup_method(self, method):
        self.decorator = FileFieldAutoChangeDelete()

    def get_model(self):
        class Model(DirtyFieldsMixin, models.Model):
            file_field = models.FileField(upload_to='foo')
            foo_field = models.CharField(max_length=32)

            class Meta(object):
                app_label = 'foo'

        return Model

    def get_empty_model(self):
        class ModelEmpty(DirtyFieldsMixin, models.Model):
            class Meta(object):
                app_label = 'foo'

        return ModelEmpty

    def test_init(self):
        decorator = FileFieldAutoChangeDelete()

        assert decorator.field_names == '*'
        assert decorator.signal is models.signals.post_save
        assert decorator.signal_name_pattern == 'post_save_{model.__name__}_changedelete_{field}'

    def test_validate_model_no_is_dirty_implementation(self):
        self.decorator.to_wrap = self.get_empty_model()
        self.decorator.to_wrap.is_dirty = None
        self.decorator.to_wrap.get_dirty_fields = None

        with pytest.raises(ValueError):
            self.decorator.validate_model()

    def test_validate_model(self):
        self.decorator.to_wrap = self.get_empty_model()

        assert self.decorator.validate_model() is None

    @mock.patch.object(DirtyFieldsMixin, 'get_dirty_fields')
    @mock.patch.object(DirtyFieldsMixin, 'is_dirty')
    def test_get_signal_function_not_dirty(
            self, mock_is_dirty, mock_get_dirty_fields):
        mock_is_dirty.return_value = False
        model = self.get_model()
        self.decorator.to_wrap = model
        self.decorator.fields = ['file_field']

        signal = self.decorator.get_signal_function()

        assert callable(signal)

        instance = model()

        assert signal(model, instance) is None
        mock_is_dirty.assert_called_once_with()
        assert not mock_get_dirty_fields.called

    @mock.patch.object(DirtyFieldsMixin, 'get_dirty_fields')
    @mock.patch.object(DirtyFieldsMixin, 'is_dirty')
    def test_get_signal_function_dirty_but_no_file(
            self, mock_is_dirty, mock_get_dirty_fields):
        mock_is_dirty.return_value = True
        mock_get_dirty_fields.return_value = {}
        model = self.get_model()
        self.decorator.to_wrap = model
        self.decorator.fields = [FieldSpec('file_field', None)]

        signal = self.decorator.get_signal_function()

        assert callable(signal)

        instance = model()

        assert signal(model, instance) is None
        mock_is_dirty.assert_called_once_with()
        mock_get_dirty_fields.assert_called_once_with()

    @mock.patch.object(DirtyFieldsMixin, 'get_dirty_fields')
    @mock.patch.object(DirtyFieldsMixin, 'is_dirty')
    def test_get_signal_function(
            self, mock_is_dirty, mock_get_dirty_fields):
        f = mock.MagicMock()
        field = mock.MagicMock()
        mock_is_dirty.return_value = True
        mock_get_dirty_fields.return_value = {'file_field': f}
        model = self.get_model()
        self.decorator.to_wrap = model
        self.decorator.fields = [FieldSpec('file_field', field)]

        signal = self.decorator.get_signal_function()

        assert callable(signal)

        instance = model(file_field='foo')

        assert signal(model, instance) is None
        mock_is_dirty.assert_called_once_with()
        mock_get_dirty_fields.assert_called_once_with()
        f.delete.assert_called_once_with(save=False)
        assert f.instance == instance
        assert f.field == field
        assert f.storage == field.storage
        assert instance.file_field == 'foo'


class TestAutoSignals(object):
    def setup_method(self, method):
        self.decorator = AutoSignals()

    def test_init(self):
        supported_signals = {
            'class_prepared',
            'm2m_changed',
            'post_delete',
            'post_init',
            'post_save',
            'pre_delete',
            'pre_init',
            'pre_save',
        }
        assert self.decorator.getter == 'get_signals'
        assert isinstance(self.decorator.signal_pool, dict)
        assert set(self.decorator.signal_pool) & supported_signals == supported_signals

    def test_validate_model_not_class(self):
        self.decorator.to_wrap = None
        with pytest.raises(TypeError):
            self.decorator.validate_model()

    def test_validate_model_not_django_model(self):
        self.decorator.to_wrap = int
        with pytest.raises(TypeError):
            self.decorator.validate_model()

    def test_validate_model_not_implementing_getter(self):
        class Foo(models.Model):
            class Meta(object):
                app_label = 'foo'

        self.decorator.to_wrap = Foo
        with pytest.raises(AttributeError):
            self.decorator.validate_model()

    def test_validate_model_not_implementing_getter_as_callable(self):
        class Foo(models.Model):
            get_signals = 'foo'

            class Meta(object):
                app_label = 'foo'

        self.decorator.to_wrap = Foo
        with pytest.raises(TypeError):
            self.decorator.validate_model()

    def test_validate_model_valid(self):
        class Foo(models.Model):
            class Meta(object):
                app_label = 'foo'

            @classmethod
            def get_signals(self):
                return []

        self.decorator.to_wrap = Foo
        assert self.decorator.validate_model() is None

    @mock.patch.object(AutoSignals, 'validate_model')
    @mock.patch.object(AutoSignals, 'connect_signals')
    def test_get_wrapper_object(self, mock_connect_signals, mock_validate_model):
        self.decorator.to_wrap = mock.sentinel.to_wrap

        assert self.decorator.get_wrapped_object() is mock.sentinel.to_wrap
        mock_connect_signals.assert_called_once_with()
        mock_validate_model.assert_called_once_with()

    @mock.patch.object(AutoSignals, 'connect_signal')
    def test_connect_signals_list(self, mock_connect_signal):
        def pre_save(sender, instance, *args, **kwwargs):
            pass

        class Foo(models.Model):
            class Meta(object):
                app_label = 'foo'

            @classmethod
            def get_signals(self):
                return [pre_save]

        self.decorator.to_wrap = Foo

        self.decorator.connect_signals()
        mock_connect_signal.assert_called_once_with(pre_save)

    @mock.patch.object(AutoSignals, 'connect_signal')
    def test_connect_signals_single(self, mock_connect_signal):
        def pre_save(sender, instance, *args, **kwwargs):
            pass

        class Foo(models.Model):
            class Meta(object):
                app_label = 'foo'

            @classmethod
            def get_signals(self):
                return pre_save

        self.decorator.to_wrap = Foo

        self.decorator.connect_signals()
        mock_connect_signal.assert_called_once_with(pre_save)

    def test_connect_signal_invalid_type(self):
        self.decorator.to_wrap = mock.sentinel.model

        with pytest.raises(TypeError):
            self.decorator.connect_signal(None)

    def test_connect_signal_no_receiver(self):
        self.decorator.to_wrap = mock.sentinel.model

        with pytest.raises(ValueError):
            self.decorator.connect_signal({})

    def test_connect_signal_cant_determine_signal(self):
        self.decorator.to_wrap = mock.sentinel.model

        def foo(*args, **kwargs):
            pass

        with pytest.raises(ValueError):
            self.decorator.connect_signal(foo)

    def test_connect_signal_invalid_signal(self):
        self.decorator.to_wrap = mock.sentinel.model

        def foo(*args, **kwargs):
            pass

        with pytest.raises(ValueError):
            self.decorator.connect_signal({
                'receiver': foo,
                'signal': 'foo',
            })

    def test_connect_signal_from_callable(self):
        mock_signal = mock.MagicMock()
        self.decorator.to_wrap = mock.sentinel.model
        self.decorator.signal_pool = {'pre_save': mock_signal}

        def foo_pre_save(*args, **kwargs):
            pass

        self.decorator.connect_signal(foo_pre_save)

        mock_signal.connect.assert_called_once_with(
            sender=mock.sentinel.model,
            receiver=foo_pre_save,
        )

    def test_connect_signal_from_dict(self):
        mock_signal = mock.MagicMock()
        self.decorator.to_wrap = mock.sentinel.model
        self.decorator.signal_pool = {'pre_save': mock_signal}

        def foo_pre_save(*args, **kwargs):
            pass

        self.decorator.connect_signal({
            'receiver': foo_pre_save,
            'weak': False,
        })

        mock_signal.connect.assert_called_once_with(
            sender=mock.sentinel.model,
            receiver=foo_pre_save,
            weak=False,
        )
