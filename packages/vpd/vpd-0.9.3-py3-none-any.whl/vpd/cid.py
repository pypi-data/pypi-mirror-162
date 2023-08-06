"""
This implementation of CaseInsensitiveDict is taken from the python requests library.

Although some modifications were made, they were generally trivial. Given the ubiquitous
nature of requests, it would've been reasonable to just depend on the upstream code, but
it seemed inappropriate to risk upstream changes breaking code with changes across versions.
This seemed extremely relevant because the previous version of this code that was used in
a few places was from an older implementation that used upper-cased keys instead of
lower-cased keys. This type of change could break augmenting code. Therefore, it made
sense to reproduce it here to prevent version-related breaking changes.

The original license and copyright are:

(c) 2017 by Kenneth Reitz.
License: Apache 2.0

"""

from collections import OrderedDict

try:
    from collections import Mapping, MutableMapping
except ImportError:
    from collections.abc import Mapping, MutableMapping


class CaseInsensitiveDict(MutableMapping):
    """A case-insensitive ``dict``-like object.

    Implements all methods and operations of
    ``MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.

    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive::

        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True

    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.

    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """

    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (cased_key for cased_key, mapped_value in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lower_key, key_val[1]) for (lower_key, key_val) in self._store.items())

    def get_item(self, key, default_key=None, default_value=None):
        """
        Alternative version of get(key, default) for a case-insensitive dict. This always return a (key, value) tuple.
        The key will be returned in its original cased form. This can be useful when filtering user input to lookup
        data. The user provided key may not match the case of the backing dict data. This allows retrieval of the
        "authoritative" key and associated value.

        :param key: key of item to retrieve
        :param default_key: default key to respond with if key not in dict
        :param default_value: default value to respond with if key not in dict
        :return: (key, value) tuple
        """
        kl = key.lower()
        return self._store[kl] if kl in self._store else (default_key, default_value)

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))
