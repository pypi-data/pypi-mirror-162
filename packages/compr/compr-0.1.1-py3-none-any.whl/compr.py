# -*- coding: utf-8 -*-
"""
Handy wrappers for advanced object comparing/matching.
"""

import re


_COMPARATORS = {}  # dict of known comparator objects


def comparator(method):
    """
    Decorator that produces `comparator` objects

    Args:
        A function that returns True of False.
        1st function argument is the value we want to measure.
        Remaining arguments would be used as compare conditions.

    Returns:
        `comparator` object where __eq__ is a wrapped function.
        Uses wrapped function for every comparison via == .
    """
    def wrap(*condition):
        def eq(self_, val): return method(val, *condition)
        def repr_(self_): return '{0}({1})'.format(
            method.__name__, ', '.join(repr(i) for i in condition))
        return type('Cmp', (), {'__eq__': eq, '__repr__': repr_})()
    wrap.__doc__ = method.__doc__
    # Store comparator to assist kwargs2cmp function
    _COMPARATORS[method.__name__] = wrap
    return wrap


# Sample handy comparators

@comparator
def within(val, a, b):
    return a <= val <= b


@comparator
def contains(val, param):
    return param in val


@comparator
def one_of(val, condition):
    return val in condition


@comparator
def lt(val, condition):
    return val < condition


@comparator
def gt(val, condition):
    return val > condition


@comparator
def le(val, condition):
    return val <= condition


@comparator
def ge(val, condition):
    return val >= condition


@comparator  # TODO: invent better names for these
def ne(val, condition):
    return not(val == condition)


@comparator
def eq_all(val, *condition):
    return all(val == i for i in condition)


@comparator
def eq_any(val, *condition):
    return any(val == i for i in condition)


@comparator
def re_search(val, pattern):
    return re.search(pattern, val) is not None


@comparator
def re_match(val, pattern):
    return re.match(pattern, val) is not None


@comparator
def endswith(val, condition):
    return val.endswith(condition)


@comparator
def eq(val, condition):  # pylint: disable=invalid-name
    return val == condition


@comparator
def contains_dict(dict_val, *args, **kwargs):
    expected_dict = dict(*args, **kwargs)
    try:
        return all(v == dict_val[k] for k, v in expected_dict.items())
    except KeyError:
        return False


# Convenience functions to assist parsing kwargs and compare agains objects

def kwargs2cmp(kwargs):
    """Convert kwargs to comparator-s list

    Args:
        kwargs (dict): a dict taken from kwargs where each item is
            <var-name>_<comparator-name>: <value>

    Returns:
        list of (<var-name>: <comparator-name>(value))
    """
    regex = re.compile(f"^(\\w+)_({'|'.join(k for k in _COMPARATORS)})")
    retval = []
    for k, v in kwargs.items():
        match_result = regex.fullmatch(k)
        if match_result:
            var, func_name = match_result.groups()
            retval.append((var, _COMPARATORS[func_name](v)))
        else:
            retval.append((k, v))

    return retval


# XXX: think about handling exceptions from comparators
def all_items(val, pairs):
    return all(k in val and val[k] == v for k, v in pairs)


def all_attrs(obj, pairs):
    return all(hasattr(obj, k) and getattr(obj, k) == v for k, v in pairs)
