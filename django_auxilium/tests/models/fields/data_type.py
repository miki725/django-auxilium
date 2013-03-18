import json
from django.test import TestCase
from django_auxilium.models.fields.data_type import DataType
from mock import MagicMock, call
from random import randrange


class TestDataType(TestCase):
    def test_init(self):
        d = DataType()
        self.assertEqual(d.datatype, unicode)

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
        non_existing = ('unicode', 'int', 'float')

        dt = DataType()

        for d, methods in existing.items():
            for m in methods:
                dt.datatype = DataType.SUPPORTED_TYPES[m]
                self.assertEqual(dt.get_custom_method(d),
                                 getattr(dt, '{}_{}'.format(d, m)))

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
            'unicode': (u'foo', u'foo'),
            'str': ('foo', u'foo'),
            'bool': (False, 'False'),
            'int': (5, u'5'),
            'float': (5.0, u'5.0'),
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
            print dt.get_custom_method('decode')
            self.assertEqual(dt.decode_bool(d), e)

    def test_decode(self):
        data = {
            'unicode': (u'foo', u'foo'),
            'str': (u'foo', 'foo'),
            'bool': ('False', False),
            'int': (u'5', 5),
            'float': (u'5.0', 5.0),
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

    def test_unicode(self):
        for d in DataType.SUPPORTED_TYPES.keys():
            dt = DataType(d)
            self.assertEqual(dt.__unicode__(), d)

    def test_str(self):
        for d in DataType.SUPPORTED_TYPES.keys():
            dt = DataType(d)
            self.assertEqual(dt.__str__(), d)

    def test_len(self):
        for d in DataType.SUPPORTED_TYPES.keys():
            dt = DataType(d)
            self.assertEqual(dt.__len__(), len(d))

    def test_call(self):
        types = ('unicode', 'str', 'bool', 'int', 'float', 'list',)

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
            print m.mock_calls
            self.assertEqual(m.mock_calls[0], call('foo'))
