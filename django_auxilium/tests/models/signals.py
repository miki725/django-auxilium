from django.db import models
from django.test import TestCase
from mock import MagicMock, call, patch
from django_auxilium.models import FileFieldAutoDelete


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
        self.signals = models.signals.post_delete.receivers
        models.signals.post_delete.receivers = []

    def connect_signals(self):
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
            f = FileFieldAutoDelete(n, n)
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
        self.assertEqual(mock.mock_calls[-1], call.file_field.delete(save=False))
        self.assertIn(call.file_field.delete(save=False), mock.mock_calls)

        # file_field not there as returned by __nonzer__() == 0
        mock = MagicMock()
        mock.file_field.__nonzero__.return_value = 0
        a(None, mock)
        self.assertLessEqual(len(mock.mock_calls), 1)
        self.assertNotIn(call.file_field.delete(save=False), mock.mock_calls)

    def test_connect_signal_function(self):
        self.disconnect_signals()
        f = FileFieldAutoDelete('file_field')
        f(self.get_model())
        self.assertEqual(len(models.signals.post_delete.receivers), 1)
        self.assertIs(models.signals.post_delete.receivers[0][1], f.get_signal_function())
        self.connect_signals()

        self.disconnect_signals()
        with patch('django.db.models.signals.post_delete') as mock:
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
        self.connect_signals()
