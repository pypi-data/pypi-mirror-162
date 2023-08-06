# author: Drew Botwinick, Botwinick Innovations
# license: 3-clause BSD
try:
    from collections import Mapping
except ImportError:
    from collections.abc import Mapping

from six import string_types


def is_iterable(obj, strings=False, mappings=False, excluded_types=None):
    """
    Python 2/3 safe check for whether a function is iterable. Python3 has better semantics for checking if iterable; this
    function is meant to be Py2/3 safe. String-types are generally excluded (often what people are trying to determine
    when checking if iterable), but option exists to include string-types to make this more accurate to its namesake.

    :param obj: object to check
    :param strings: whether to consider strings as "iterable" for the purposes of this function
    :param mappings: whether to consider Mappings as "iterable" for the purposes of this function
    :param excluded_types: callable single-arg function or iterable of other types to exclude from considering iterable
    :return: True if iterable
    """
    if isinstance(obj, string_types) and not strings:
        return False
    elif isinstance(obj, Mapping) and not mappings:
        return False
    elif callable(excluded_types) and excluded_types(obj):
        return False
    elif excluded_types and is_iterable(excluded_types) and isinstance(obj, tuple(excluded_types)):
        return False
    elif isinstance(obj, string_types):
        return True

    # TODO: I have abc-derived extension code that worked on py2.7 that I need to find that can replace this... and be compat for py2/3
    # noinspection PyBroadException
    try:
        iter(obj)
    except BaseException:
        return False

    return True


def flatten(iterable, max_depth=None, enumeration=False, excluded_types=None):
    """
    Flatten nested iterables into a single generator that yields items. max_depth parameter can be useful but
    it's a bit flaky / written quickly without really thinking it through or testing it beyond a few minimal
    use cases. The max_depth might be off by 1 for what you expect, but should generally work... give it a shot.

    TODO: clean-up code
    TODO: fix max_depth

    :param iterable:
    :param max_depth:
    :type max_depth: None|int
    :param enumeration: whether to mimic enumerate(flatten(...)) where the enumeration is tied to the top-level iterable.
    :param excluded_types: types to exclude from flattening
    :return: generator that yields values
    """
    if max_depth is not None:
        max_depth -= 1
    if max_depth is not None and max_depth <= 0:
        yield iterable

    if not is_iterable(iterable, excluded_types=excluded_types):
        yield iterable
    else:  # TODO: clean this up... it got messy
        for k, item in enumerate(iterable):
            if is_iterable(item, excluded_types=excluded_types) and (max_depth is None or max_depth > 0):
                # noinspection PyTypeChecker
                for sub_item in flatten(item, None if max_depth is None else max_depth - 1, enumeration=False):  # max_depth
                    if enumeration:  # future: int for enumeration means target depth for enumeration???
                        yield k, sub_item
                    else:
                        yield sub_item
            elif enumeration:  # future: int for enumeration means target depth for enumeration???
                yield k, item
            else:
                yield item
