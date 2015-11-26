from __future__ import print_function, unicode_literals

import pytest

from django_auxilium.utils.range import AlphabeticNumbers, Range


class TestAlphabeticNumbers(object):
    def test_int_from_str(self):
        data = [
            ('A', 1),
            ('Z', 26),
            ('AA', 27),
            ('BA', 53),
            ('AAA', 703),
            ('XZZ', 16926),
            ('ZZZ', 18278),
        ]
        for d in data:
            assert AlphabeticNumbers.int_from_str(d[0]) == d[1]

    def test_str_from_int(self):
        data = [
            ('A', 1),
            ('Z', 26),
            ('AA', 27),
            ('BA', 53),
            ('AAA', 703),
            ('XZZ', 16926),
            ('ZZZ', 18278),
        ]
        for d in data:
            assert AlphabeticNumbers.str_from_int(d[1]) == d[0]

        for i in [0, -1]:
            with pytest.raises(ValueError):
                AlphabeticNumbers.str_from_int(i)


def test_range_columns():
    assert Range(0, 1, 2, 3).columns == 0
    assert Range(1, 1, 2, 3).columns == 2


def test_range_rows():
    assert Range(0, 0, 2, 3).rows == 0
    assert Range(0, 1, 2, 2).rows == 2
