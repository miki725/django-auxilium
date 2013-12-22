from __future__ import unicode_literals, print_function
import json
import six
from django.test import TestCase
from django_auxilium.models.fields.data_type import DataType
from mock import MagicMock, call
from random import randrange


class TestDataType(TestCase):
    def test_init(self):
        d = DataType()
        self.assertEqual(d.datatype, six.text_type)

        for k, t in DataType.SUPPORTED_TYPES.items():
            d = DataType(k)
            self.assertEqual(d.datatype, t)

        for t in DataType.SUPPORTED_TYPES.values():
            d = DataType(t)
            self.assertEqual(d.datatype, t)

        for t in ('foo', 'bar',):
            with self.assertRaises(TypeError):
                DataType(t)

    def test_get_custom_method(self):
        existing = {
            'encode': ('list',),
            'decode': ('list', 'bool'),
        }
        non_existing = ('text', 'int', 'float')

        dt = DataType()

        for d, methods in existing.items():
            for m in methods:
                dt.datatype = DataType.SUPPORTED_TYPES[m]
                self.assertEqual(dt.get_custom_method(d),
                                 getattr(dt, '{0}_{1}'.format(d, m)))

        for d in ['encode', 'decode']:
            for m in non_existing:
                dt.datatype = DataType.SUPPORTED_TYPES[m]
                self.assertIsNone(dt.get_custom_method(d))

    def test_encode_list(self):
        data = [randrange(0, 1000) for i in range(20)]
        expected = json.dumps(data)
        dt = DataType('list')

        self.assertEqual(dt.encode_list(data), expected)

    def test_encode(self):
        data = {
            'text': ('foo', 'foo'),
            'bool': (False, 'False'),
            'int': (5, '5'),
            'float': (5.0, '5.0'),
            'list': (['foo', 'bar'], json.dumps(['foo', 'bar'])),
        }

        for d, values in data.items():
            dt = DataType(d)
            value, expected = values
            self.assertEqual(dt.encode(value), expected)

        # make sure the ``get_custom_method`` is called
        for d, values in data.items():
            dt = DataType(d)
            value, expected = values
            m = MagicMock()
            dt.get_custom_method = m
            dt.encode(value)
            self.assertGreater(len(m.mock_calls), 0)
            self.assertEqual(m.mock_calls[2], call()(value))

    def test_decode_list(self):
        expected = [randrange(0, 1000) for i in range(20)]
        data = json.dumps(expected)
        dt = DataType('list')

        self.assertEqual(dt.decode_list(data), expected)

    def test_decode_bool(self):
        data = ('True', 'False', 'foo')
        expected = (True, False, False)
        dt = DataType('bool')

        for d, e in zip(data, expected):
            self.assertEqual(dt.decode_bool(d), e)

    def test_decode(self):
        data = {
            'text': ('foo', 'foo'),
            'bool': ('False', False),
            'int': ('5', 5),
            'float': ('5.0', 5.0),
            'list': (json.dumps(['foo', 'bar']), ['foo', 'bar']),
        }

        for d, values in data.items():
            dt = DataType(d)
            value, expected = values
            self.assertEqual(dt.decode(value), expected)

        # make sure the ``get_custom_method`` is called
        for d, values in data.items():
            dt = DataType(d)
            value, expected = values
            m = MagicMock()
            dt.get_custom_method = m
            dt.encode(value)
            self.assertGreater(len(m.mock_calls), 0)
            self.assertEqual(m.mock_calls[-1], call()(value))

    def test_str(self):
        for d in DataType.SUPPORTED_TYPES.keys():
            dt = DataType(d)
            self.assertEqual(six.text_type(dt), d)

    def test_len(self):
        for d in DataType.SUPPORTED_TYPES.keys():
            dt = DataType(d)
            self.assertEqual(dt.__len__(), len(d))

    def test_call(self):
        types = ('text', 'bool', 'int', 'float', 'list',)

        for t in types:
            dt = DataType(t)
            self.assertTrue(callable(dt))

            m = MagicMock()
            dt.decode = m
            self.assertEqual(dt(), t)
            self.assertEqual(len(m.mock_calls), 0)

            m = MagicMock()
            dt.decode = m
            self.assertNotEqual(dt('foo'), t)
            self.assertEqual(m.mock_calls[0], call('foo'))
