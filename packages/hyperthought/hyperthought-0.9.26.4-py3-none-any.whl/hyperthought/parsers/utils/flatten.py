"""
Flatten nested structures to a flat dictionary.

Nested dictionaries (actually dict-like objects) will be flattened by using
path syntax.
    Ex: {'a': 'b': {'c': 'test'} => {'a/b/c': 'test'}

Nested lists (actually list-like object) will be flattened by using indices.
    Ex: {'a': [1, 2, 3]} => {'a_0': 1, 'a_1': 2, 'a_2': 3}
"""

import collections


KEY_SEP = '/'           # Separator between keys in nested dicts.
INDEX_SEP = '_'         # Separator between key path and list index.
ROOT_LIST_KEYPATH = ''  # Root-level keypath used when processing lists.


def flatten(data):
    """Flatten data to a non-nested structure."""
    output = {}

    if isinstance(data, collections.abc.Mapping):
        _flatten_mapping(data, output)
    elif (not isinstance(data, str)
          and isinstance(data, collections.abc.Sequence)):
        _flatten_sequence(data, output, key_path=ROOT_LIST_KEYPATH)
    else:
        raise TypeError('Invalid type for data parameter.'
                        'Expected dict-like or list-like.')

    return output


def _flatten_sequence(data, output, key_path):
    for index in range(len(data)):
        new_key_path = '{}{}{}'.format(key_path, INDEX_SEP, index)

        if isinstance(data[index], collections.abc.Mapping):
            _flatten_mapping(data[index], output, new_key_path)
        elif (not isinstance(data[index], str)
              and isinstance(data[index], collections.abc.Sequence)):
            _flatten_sequence(data[index], output, new_key_path)
        else:
            output[new_key_path] = data[index]


def _flatten_mapping(data, output, key_path=None):
    prefix = '' if key_path is None else key_path + KEY_SEP

    for key in data:
        new_key_path = prefix + key

        if isinstance(data[key], collections.abc.Mapping):
            _flatten_mapping(data[key], output, new_key_path)
        elif (not isinstance(data[key], str)
              and isinstance(data[key], collections.abc.Sequence)):
            _flatten_sequence(data[key], output, new_key_path)
        else:
            output[new_key_path] = data[key]
