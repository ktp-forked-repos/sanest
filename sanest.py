"""
sanest, sane nested dictionaries and lists
"""

import collections.abc

TYPES = [bool, float, int, str]


class InvalidKeyError(TypeError):
    """
    Exception indicating that an invalid key is passed.

    This is a subclass of the built-in ``TypeError``, since this
    indicates problematic code that uses an incorrect API.

    Despite the name, it does not indicate absence of an item in a
    dictionary (which is what ``KeyError``) would indicate.
    """
    pass


class InvalidValueTypeError(TypeError):
    """
    Exception indicating that the requested type is invalid.

    This is a subclass of the built-in ``TypeError``, since this
    indicates problematic code that uses an incorrect API.
    """
    pass


class InvalidValueError(ValueError):
    """
    Exception indicating that the data structure does not match what the
    code expects.

    This is a subclass of the built-in ``ValueError``, since this
    indicates malformed data.
    """
    pass


def parse(key):
    path = []
    if isinstance(key, (tuple, list)):
        # nested lookup and typed nested lookup,
        # e.g. d['a','b'] and  d['a','b':str]
        try:
            *path, key = key
        except ValueError:
            raise InvalidKeyError("empty path: {!r}".format(key))
    if isinstance(key, str):
        # basic lookup, e.g. d['a']
        value_type = None
    elif isinstance(key, slice):
        # typed lookup, e.g. d['a':str]
        if key.step is not None:
            raise InvalidKeyError(
                "slice cannot contain step value: {!r}".format(key))
        if not key.start:
            raise InvalidKeyError("key is empty: {!r}".format(key))
        value_type = key.stop
        key = key.start
    else:
        raise InvalidKeyError("unknown type: {!r}".format(key))
    path.append(key)
    return path, value_type


def check_type(x, expected_type):
    if not isinstance(x, expected_type):
        raise InvalidValueError(
            "requested {.__name__}, got {.__name__}: {!r}"
            .format(expected_type, type(x), x))


def resolve_path(obj, path):
    for n, key_or_index in enumerate(path, 1):
        if not isinstance(key_or_index, (str, int)):
            raise InvalidKeyError(
                "path must contain only str or int: {!r}".format(path))
        if isinstance(key_or_index, str) and not isinstance(obj, Mapping):
            raise InvalidValueError("subpath is not a dict: {!r}", path[:n])
        if isinstance(key_or_index, int) and not isinstance(obj, Sequence):
            raise InvalidValueError("subpath is not a list: {!r}", path[:n])
        obj = obj[key_or_index]
    return obj


def lookup(obj, *, path, value_type):
    if value_type is not None and value_type not in TYPES:
        raise InvalidValueTypeError(
            "type must be one of {}"
            .format(', '.join(t.__name__ for t in TYPES)))
    obj = resolve_path(obj, path)
    if value_type is not None:
        check_type(obj, value_type)
    return obj


class Mapping(collections.abc.Mapping):
    __slots__ = ('_data',)

    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        if isinstance(key, str):  # trivial lookup
            return self._data[key]
        path, value_type = parse(key)
        return lookup(self, path=path, value_type=value_type)

    def get(self, key, default=None, *, type=None):
        value = super().get(key, default)
        if type is not None and value is not default:
            check_type(value, type)
        return value

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    # todo: typed __contains__(). maybe .contains() with type= arg?
    #       maybe something like "('a', 'b', str) in d"?
    # todo: type checking views? (how?)


class MutableMapping(Mapping, collections.abc.MutableMapping):
    __slots__ = ()

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise InvalidKeyError("invalid key: {!r}".format(key))
        # todo: convert dict/list values into own mapping types
        # todo: nested setitem
        # todo: typed setitem
        self._data[key] = value

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise InvalidKeyError("invalid key: {!r}".format(key))
        # todo: nested delitem
        # todo: typed delitem
        del self._data[key]

    def clear(self):
        self._data.clear()

    # todo: clean api for building nested structures
    # todo: autovivification
    # todo: .setdefault() with type= arg
    # todo: .pop() with type= arg
    # todo: .popitem() with type= arg
    # todo: support for copy.copy() and copy.deepcopy()
    # todo: .copy(deep=True)
    # todo: pickle support
    # todo: disallow None values. "d['x'] = None" means "del d['x']"?


# todo: support for lists

class Sequence(collections.Sequence):
    # todo: implement

    def __getitem__(self, index):
        if isinstance(index, int):
            return self._data[index]
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class MutableSequence(Sequence, collections.abc.MutableSequence):
    # todo: implement

    def __setitem__(self, index, value):
        raise NotImplementedError

    def insert(self, index, value):
        raise NotImplementedError

    def __delitem__(self, index):
        raise NotImplementedError


# friendly names
# todo: lowercase names? must not mask built-names 'dict' and
# 'list' since those are used elsewhere in this module.
Dict = MutableMapping
List = MutableSequence
