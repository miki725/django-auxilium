import random
from django.test import TestCase
from django_auxilium.utils.range import AlphabeticNumbers


class AlphabeticNumbers_Test(TestCase):
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
            self.assertEqual(AlphabeticNumbers.int_from_str(d[0]), d[1])

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
            self.assertEqual(AlphabeticNumbers.str_from_int(d[1]), d[0])

        for i in [0, -1]:
            with self.assertRaises(ValueError):
                AlphabeticNumbers.str_from_int(i)

    def testRandom(self):
        for i in range(1000):
            number = random.randint(1, 1000000000)
            self.assertEqual(
                AlphabeticNumbers.int_from_str(AlphabeticNumbers.str_from_int(number)),
                number
            )
