def try_int(value):
    """
    Tries to convert a value into an integer. If it fails it returns "None" instead of erroring.

    Parameters
    ----------
    value: any
        The value to try and convert to an int

    Returns
    -------
    int:
        The value converted to an int
    None:
        If the value could not be converted then it will return "None"

    Examples
    --------
    >>> try_int("1")
    1
    >>> try_int([1, 2, 3])
    None
    """
    if not value:
        return None
    try:
        return int(value)
    except TypeError:
        return None


def try_str(value):
    """
    Tries to convert a value into an string. If it fails it returns "None" instead of erroring.

    Parameters
    ----------
    value: any
        The value to try and convert to an string

    Returns
    -------
    str:
        The value converted to an str
    None:
        If the value could not be converted then it will return "None"

    Examples
    --------
    >>> try_str(1)
    "1"
    >>> try_str([1, 2, 3])
    None
    """
    if not value:
        return None
    try:
        return str(value)
    except TypeError:
        return None
