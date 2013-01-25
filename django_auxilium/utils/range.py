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

        # recursive method
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
                number = number / 26 - 1
            else:
                string += chr(remainder + 64)
                number /= 26
            if number < 1:
                break

        return string[::-1]


def get_range_num_cols(range_value):
    """
    Gets the number of columns in a given range.

    Parameters
    ----------
    range_value : array
        The range to calculate the number of columns

    Returns
    -------
    columns : int
        The number of columns

    """
    if range_value[0]:
        return range_value[2] - range_value[0] + 1
    return 0


def get_range_num_rows(range_value):
    """
    Gets the number of rows in a given range.

    Parameters
    ----------
    range_value : array
        The range to calculate the number of rows

    Returns
    -------
    rows : int
        The number of rows
    """
    if range_value[1]:
        return range_value[3] - range_value[1] + 1
    return 0


def get_range_diag(range_value):
    """
    Gets the length of the diagonal in a given range.

    Parameters
    ----------
    range_value : array
        The range to calculate the length of the diagonal

    Returns
    -------
    length : int
        The length of the diagonal
    """
    import math

    n_rows = get_range_num_rows(range_value)
    n_cols = get_range_num_cols(range_value)
    return math.sqrt(n_rows ** 2 + n_cols ** 2)
