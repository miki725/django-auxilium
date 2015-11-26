from __future__ import unicode_literals

import six


def get_content_type_from_binary(data):
    """
    Get content_type of a binary string by using ``magic`` library

    Parameters
    ----------
    data : binary
        Binary string data of a file from which
        content_type will be determined

    Returns
    -------
    str
        Content-type of a file as string
    """
    # has to be inline import since this lib does not
    # required python-magic by default.
    import magic

    return magic.from_buffer(data, mime=True).decode('utf-8')


def get_content_type_from_file(f):
    """
    Get content_type of a file-like object by using ``magic`` library

    .. note::
        This function reads first 1Kb of the file in order
        to determine the content_type however at the end
        seeks back to ``0``

    Parameters
    ----------
    f : file
        File-like object which should implement
        ``.seek()`` and ``.read()`` methods
        from which content_type will be determined

    Returns
    -------
    str
        Content-type of a file as string
    """
    f.seek(0)
    try:
        return get_content_type_from_binary(f.read(1024))
    finally:
        f.seek(0)


def get_content_type(f):
    """
    Get content_type of a file by using ``magic`` library

    Parameters
    ----------
    f : str or file
        Either a binary string of a file content or a
        file-like object from which file data will be read

    Returns
    -------
    str
        Content-type of a file as string


    See Also
    --------
    get_content_type_from_binary
    get_content_type_from_file
    """
    if isinstance(f, six.binary_type):
        return get_content_type_from_binary(f)
    else:
        return get_content_type_from_file(f)
