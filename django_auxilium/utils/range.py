from __future__ import division, print_function, unicode_literals
from collections import namedtuple


class Range(namedtuple('rangenamedtuple', ['first_column', 'first_row', 'second_column', 'second_row'])):
    """
    Helper data-structure for storing excel-type ranges.

    Also has some useful range-related properties
    """

    @property
    def columns(self):
        """
        Gets the number of columns in a given range.

        Returns
        -------
        columns : int
            The number of columns
        """
        if self.first_column and self.second_column:
            return self.second_column - self.first_column + 1
        return 0

    @property
    def rows(self):
        """
        Gets the number of columns in a given range.

        Returns
        -------
        columns : int
            The number of columns
        """
        if self.first_row and self.second_row:
            return self.second_row - self.first_row + 1
        return 0


class AlphabeticNumbers(object):
    """
    Utility class for dealing with numbers in alphabetical form. Useful for converting
    Excel column notation into numbers and vise verse.
    """

    @staticmethod
    def int_from_str(string):
        """
        Convert alphabetical number into actual integer.

        Parameters
        ----------
        string : str
            Number in alphabetical form (e.g. AB = 28)

        Returns
        -------
        number : int
            Converted integer value
        """
        string = string.upper()[::-1]
        number = 0
        for i, c in enumerate(string):
            number += (ord(c) - 64) * (26 ** i)
        return number

    @staticmethod
    def str_from_int(number):
        """
        Convert integer into its alphabetical representation.

        Parameters
        ----------
        number : int
            Number to be converted

        Returns
        -------
        string : str
            The alphabetical representation of the number

        Raises
        ------
        ValueError
            If the input number is not valid
        """

        if number < 1:
            raise ValueError('Invalid Number')

        string = ''

        # recursive method for education purposes
        # however regular loop is used due to better performance
        #
        # if number < 27:
        #     return chr(number + 64)
        # else:
        #     remainder = number % 26
        #     if not remainder:
        #         return AlphabeticNumbers.str_from_int(int(number / 26) - 1) + 'Z'
        #     else:
        #         return AlphabeticNumbers.str_from_int(int(number / 26)) + chr(remainder + 64)

        while True:
            remainder = number % 26
            if not remainder:
                string += 'Z'
                number = number // 26 - 1
            else:
                string += chr(remainder + 64)
                number //= 26
            if number < 1:
                break

        return string[::-1]
