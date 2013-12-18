from __future__ import unicode_literals, print_function
from django.db import models
from django.test import TestCase
from django_auxilium.models import (FileFieldAutoDelete,
                                    FileFieldAutoChangeDelete,
                                    AutoSignals)
from mock import MagicMock, call
from random import randint
import six


class TestFileFieldAutoDelete(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = FileFieldAutoDelete.to_decorator()('file_field')

    def get_model(self):
        class Model(models.Model):
            file_field = models.FileField(upload_to='foo')
            foo_field = models.CharField(max_length=32)

        return Model

    def get_empty_model(self):
        class ModelEmpty(models.Model):
            pass

        return ModelEmpty

    def get_empty_class(self):
        class Foo(object):
            pass

        return Foo

    def disconnect_signals(self):
        """
        Remove signals connected by Django
        """
        self.signals = models.signals.post_delete.receivers
        models.signals.post_delete.receivers = []

    def restore_signals(self):
        """
        Restore signals connected by Django
        """
        models.signals.post_delete.receivers = self.signals
        self.signals = []

    def test_get_wrapped_object(self):
        m = self.get_model()
        self.assertIs(self.f(m), m)

    def test_validate_model(self):
        m = 'This decorator can only be applied to classes'
        with self.assertRaisesMessage(TypeError, m):
            self.f(None)

        m = 'Decorator can only be applied to Django models'
        with self.assertRaisesMessage(TypeError, m):
            self.f(self.get_empty_class())

        m = 'Field "file_field" must be a subclass of Django ``FileField``'
        with self.assertRaisesMessage(TypeError, m):
            self.f(self.get_empty_model())

        m = 'Field "foo_field" must be a subclass of Django ``FileField``'
        with self.assertRaisesMessage(TypeError, m):
            FileFieldAutoDelete('foo_field')(self.get_model())

    def test_get_signal_name(self):
        names = ('foo', 'bar',)
        for n in names:
            f = FileFieldAutoDelete(n, signal_name_pattern=n)
            f.to_wrap = None
            self.assertEqual(f.get_signal_name(), n)

            f = FileFieldAutoDelete(n)

            class foo(object):
                def __getattribute__(self, item):
                    if item == '__name__':
                        return n
                    else:
                        return object.__getattribute__(self, item)

            f.to_wrap = foo()
            self.assertEqual(f.get_signal_name(), 'post_delete_{0}_delete_{0}'.format(n))

    def test_get_signal_function(self):
        # check cache
        f = FileFieldAutoDelete('file_field')
        a = f.get_signal_function()
        b = f.get_signal_function()
        self.assertIs(a, b)

        # with file_field
        mock = MagicMock()
        a(None, mock)
        self.assertGreater(len(mock.mock_calls), 1)
        self.assertIn(call.file_field.delete(save=False), mock.mock_calls)

        # file_field not there as returned by __nonzero__() == 0
        mock = MagicMock()
        try:
            mock.file_field.__nonzero__.return_value = 0   # Python 2
        except AttributeError:
            mock.file_field.__bool__.return_value = False  # Python 3
        a(None, mock)
        self.assertEqual(len(mock.mock_calls), 1)
        self.assertNotIn(call.file_field.delete(save=False), mock.mock_calls)

    def test_connect_signal_function(self):
        self.disconnect_signals()
        f = FileFieldAutoDelete('file_field')
        f(self.get_model())
        self.assertEqual(len(models.signals.post_delete.receivers), 1)
        self.assertIs(models.signals.post_delete.receivers[0][1], f.get_signal_function())
        self.restore_signals()

        self.disconnect_signals()
        mock = MagicMock()
        f = FileFieldAutoDelete('file_field', signal=mock)
        m = self.get_model()
        f(m)
        self.assertEqual(len(mock.mock_calls), 1)
        self.assertEqual(mock.mock_calls[0],
                         call.connect(
                             f.get_signal_function(),
                             weak=False,
                             dispatch_uid='post_delete_Model_delete_file_field',
                             sender=m
                         ))
        self.restore_signals()


class TestFileFieldAutoChangeDelete(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = FileFieldAutoChangeDelete.to_decorator()('file_field')

    def get_model(self):
        class Model(models.Model):
            file_field = models.FileField(upload_to='foo')
            foo_field = models.CharField(max_length=32)

        return Model

    def test_validate_model(self):
        m = self.get_model()

        with self.assertRaises(ValueError):
            self.f(m)

        for f in ['is_dirty', 'get_dirty_fields']:
            g = lambda this: None
            setattr(m, f, g.__get__(m, m.__class__))

            with self.assertRaises(ValueError):
                self.f(m)

            delattr(m, f)

        for f in ['is_dirty', 'get_dirty_fields']:
            g = lambda this: None
            setattr(m, f, g.__get__(m, m.__class__))

        self.assertTrue(True)

    def test_get_signal_function(self):
        # check cache
        f = FileFieldAutoChangeDelete('file_field')
        a = f.get_signal_function()
        b = f.get_signal_function()
        self.assertIs(a, b)

        # with file_field
        mock = MagicMock()
        a(None, mock)
        self.assertIn(call.is_dirty, mock.mock_calls)
        self.assertIn(call.get_dirty_fields().get('file_field', None),
                      mock.mock_calls)
        self.assertIn(call.get_dirty_fields().get().delete(save=False),
                      mock.mock_calls)

        mock = MagicMock()
        mock.get_dirty_fields.return_value = {}
        a(None, mock)
        self.assertNotIn(call.get_dirty_fields().get().delete(save=False),
                         mock.mock_calls)


class TestAutoSignals(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = AutoSignals()

    def test_validate_model(self):
        d = AutoSignals()
        d.connect_signals = lambda: None

        with self.assertRaises(TypeError):
            d(None)

        class Foo(object):
            pass

        with self.assertRaises(TypeError):
            d(Foo)

        class Foo(models.Model):
            pass

        with self.assertRaises(ValueError):
            d(Foo)

        class Bar(models.Model):
            get_signals = ''

        with self.assertRaises(ValueError):
            d(Bar)

        class Cat(models.Model):
            def get_signals(self):
                pass

        d(Cat)
        self.assertTrue(True)

    def test_get_wrapper_object(self):
        d = AutoSignals()
        d.validate_model = MagicMock()
        d.connect_signals = MagicMock()
        d.to_wrap = None

        d.get_wrapped_object()

        self.assertTrue(d.validate_model.called)
        self.assertTrue(d.connect_signals.called)

    def test_connect_signals(self):
        ref = randint(1, 100)

        obj = MagicMock()
        obj.get_signals.return_value = ref
        connect = MagicMock()

        d = AutoSignals()
        d.to_wrap = obj
        d.connect_signal = connect
        d.connect_signals()

        obj.get_signals.assert_called_with()
        connect.assert_called_with(ref)

    def test_connect_signal(self):
        to_wrap = MagicMock()
        signal = MagicMock()
        receiver = MagicMock()
        receiver.__name__ = 'foo_dog'
        receiver.return_value = ''

        d = AutoSignals(signal_pool={'dog': signal})
        d.to_wrap = to_wrap
        d.connect_signal(receiver)
        expected = {
            'receiver': receiver,
            'sender': to_wrap,
        }

        signal.connect.assert_called_with(**expected)

        # -----------------

        to_wrap = MagicMock()
        signal = MagicMock()
        receiver = MagicMock()
        weak = bool(randint(0, 1))
        uid = 'foo' + six.text_type(randint(0, 100))

        d = AutoSignals()
        d.to_wrap = to_wrap
        d.connect_signal({
            'signal': signal,
            'receiver': receiver,
            'weak': weak,
            'dispatch_uid': uid
        })
        expected = {
            'receiver': receiver,
            'weak': weak,
            'dispatch_uid': uid,
            'sender': to_wrap,
        }

        signal.connect.assert_called_with(**expected)

        # -----------------

        to_wrap = MagicMock()
        d.to_wrap = to_wrap
        with self.assertRaises(TypeError):
            d.connect_signal('')

        # -----------------

        to_wrap = MagicMock()
        receiver = MagicMock()
        receiver.__name__ = 'foo'
        d.to_wrap = to_wrap
        with self.assertRaises(ValueError):
            d.connect_signal({
                'receiver': receiver
            })

        # -----------------

        to_wrap = MagicMock()
        receiver = MagicMock()
        receiver.__name__ = 'foo_bar'
        signal = MagicMock()
        d = AutoSignals(signal_pool={'bar': signal})
        d.to_wrap = to_wrap
        d.connect_signal({
            'receiver': receiver
        })
        signal.connect.assert_called_with(sender=to_wrap,
                                          receiver=receiver)

        # -----------------

        to_wrap = MagicMock()
        receiver = MagicMock()
        d = AutoSignals()
        d.to_wrap = to_wrap
        with self.assertRaises(KeyError):
            d.connect_signal({
                'signal': 'bar',
                'receiver': receiver
            })
