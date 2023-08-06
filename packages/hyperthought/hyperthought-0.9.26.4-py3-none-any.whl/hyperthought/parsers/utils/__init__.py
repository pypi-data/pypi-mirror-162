from . import flatten


def separate_units(value_and_units):
    """
    Separate values and units from a string.

    Parameters
    ----------
    value_and_units : str
        A string containing a value and units.

    Returns
    -------
    A tuple of strings containing value and units.
    """
    # TODO:  Find a better way to do this.  (Use regex.)
    n_unit_chars = 0

    for char in reversed(value_and_units.lower()):
        if char.isspace():
            break
        else:
            n_unit_chars += 1

    split_index = len(value_and_units) - n_unit_chars
    units = value_and_units[split_index:]
    value = value_and_units[:split_index].strip()
    return value, units
