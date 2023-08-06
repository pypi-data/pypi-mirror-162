# author: Drew Botwinick, Botwinick Innovations
# license: 3-clause BSD
import collections
from os import path as osp

import yaml
from six import iteritems, string_types

from .arguments import arg_substitute


def read_yaml(path, origin=None, return_path=False, windows_pseudo_links=True):
    """
    extended function to read yaml files and potentially augment the source path relative to another path and/or return the path
    :param path:
    :param origin:
    :param return_path: whether to return the path
    :param windows_pseudo_links: whether to try to follow text files that contain an alternative path (i.e. fake symlinks for windows)
    :return:
    """
    if not origin:
        path = osp.abspath(path)
    else:
        path = osp.abspath(osp.join(origin, path))  # TODO: are there any absolute/relative path considerations we need here?

    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    path = osp.dirname(path)

    # Windows symlink checking--if file content is just a string and can evaluate to a path when combined with the
    # file origin/path--then that means we're likely looking at a fake symlink style thing... and we should try following it
    if windows_pseudo_links and isinstance(data, string_types):
        try:
            dp2 = read_yaml(data, path, return_path=True, windows_pseudo_links=True)
            data, path = dp2
        except IOError:
            pass

    if not return_path:
        return data
    return data, path


def shallow_merge_dicts(*data_dicts, **kwargs):
    """
    shallow merge dictionaries. Merges dictionaries at depth=1.

    NOTE: functionality is shaky. check that it works for your use case.

    :param data_dicts: dictionaries to merge
    :param kwargs: keyword arguments
     arg: skip_none_values: default True, whether or not to skip None values
     arg: add_lists: default False, whether or not lists should be combined/added together if both entries for merge are lists
    :return: merged dictionary
    """
    skip_none_values = kwargs.get('skip_none_values', True)
    add_lists = kwargs.get('add_lists', False)

    result = dict()
    for include in data_dicts:
        if not isinstance(include, collections.Mapping):  # skip non-dictionary inputs (intended for filtering Nones etc.)
            continue
        # result.update({k: v for (k, v) in include.iteritems() if v is not None or not skip_none_values})
        for k, v in iteritems(include):
            if v is not None or not skip_none_values:
                # if we're adding lists and we've already got a list and the next thing is another one, then add
                if add_lists and k in result and isinstance(result[k], list) and isinstance(v, list):
                    result[k] += v
                else:  # otherwise (normal condition) - just set
                    result[k] = v
    return result


def get_data(sub_dict, cwd=None):
    """
    sneaky component for grabbing "sub-dict" data with builtin support for external yaml sources and including external files

    :param sub_dict:
    :param cwd:
    :return:
    """
    if not isinstance(sub_dict, collections.Mapping):
        return None

    data = dict(sub_dict)  # operate on a shallow copy

    if 'source' in data:  # then use external data
        data = get_data(*read_yaml(data['source'], cwd, return_path=True))
    elif 'include' in data:  # merge external data
        includes = data.pop('include')
        if isinstance(includes, string_types):
            includes = [includes]
        data = shallow_merge_dicts(*([get_data(*read_yaml(include, cwd, return_path=True)) for include in includes] + [data]))
    return data


def vpd_chain(*mappings):
    """
    Convenience function to generate a VirtualPathDictChain chain. Essentially
    a cascading wrapper around many dicts so that values can be pulled from the first mapping
    that provides a suitable value going in priority order from first to last.

    Also supports get/put access to nested values (see `VirtualPathDictChain`)

    :param mappings: priority sorted mappings to get values from
    :return: VirtualPathDictChain
    :rtype: VirtualPathDictChain
    """
    vpd = None
    for mapping in reversed(mappings):
        if isinstance(mapping, VirtualPathDictChain):
            for sub_map in reversed(_unchain_vpd(mapping)):
                vpd = VirtualPathDictChain(sub_map, vpd)
        elif isinstance(mapping, collections.Mapping):
            vpd = VirtualPathDictChain(mapping, vpd)
        elif mapping is not None:
            raise ValueError('all arguments must either be Mappings or VirtualPathDictChains')
    return vpd


def _unchain_vpd(vpd):
    # noinspection PyProtectedMember
    data = vpd._data
    # noinspection PyProtectedMember
    fallback = vpd._fallback
    mappings = []
    if data is not None:
        mappings.append(data)
    if fallback is not None:
        mappings.extend(_unchain_vpd(fallback))
    return mappings


def vpd_get(vpd, key, default=None, do_substitute=False, ff=None):
    """
    Augmented get function for VirtualPathDictChain objects. For the moment, this was placed outside of the
    VirtualPathDictChain class to maintain backwards compatibility for existing uses of the class. Future review
    might move this function as a replacement for the vanilla `get` function.

    :param vpd: VirtualPathDictChain object
    :param key: the key to search [ e.g. ('depth0', 'depth1', 'depth2', 'key') or 'depth0/depth1/depth2/key') ]
    :param default: default value to provide as an alternative to None
    :param do_substitute: whether or not to use vpd-inherent calls for argument substitution
    :param ff: filter_fn; lambda fn or otherwise that will be applied to the output (useful for ensuring type inferences, etc.)
    :return: resulting value
    """
    value = vpd.get(key, do_substitute=do_substitute)
    if value is None:  # TODO: disambiguate None response or lack of response?
        value = default
    if callable(ff):
        value = ff(value)
    return value


class VirtualPathDictChain(object):
    """
    Nested dict of dicts that also contains functionality for accessing nested dict data
    by using string keys with divided by '/' or as a tuple/list of keys.

    Example:
        vpd = VirtualPathDictChain({ "key1": { "nested1": "value6", "nested2": "value7" } })
        vpd.get("key1/nested2") --> "value7"

    It also supports a fallback data source (also a VPD-chain). The original design was intended for
    a over-writable settings mechanism. There could be default (or upstream) settings that are selectively
    overridden by local settings.
    """
    _data = None
    _fallback = None  # type: VirtualPathDictChain

    def __init__(self, data, fallback):
        assert isinstance(fallback, VirtualPathDictChain) or fallback is None
        self._data = data
        self._fallback = fallback

    # TODO: add cascade_enable/disable option? (to prevent falling back to fallback store...)
    # TODO: add default?
    def get(self, key, from_default=False, do_substitute=False):
        """
        load settings using the given key, automatically cascades to default settings if necessary,
        loading default without checking current settings is available via parameter

        :param key: iterable with key parts OR path-like separated string (using / as delimiter)
        :param from_default: whether to load value from fallback source. custom always cascades to default
        :param do_substitute: whether or not to automatically substitute variables embedded in strings (default=False)
        """
        if isinstance(key, string_types):
            target = key.split('/')
        elif isinstance(key, (tuple, list)):
            target = key
        else:
            return None
        result = self._get(target, from_default)
        if do_substitute and isinstance(result, string_types):
            # bit ridiculous, but let's us handle nested substitutions;
            # downside is minimum 1 extraneous call to arg_substitute + loop logic
            last_result = None
            result = arg_substitute(result, self)
            while last_result != result:
                last_result = result
                result = arg_substitute(result, self)
        return result

    def get_path(self, key, from_default=False, do_substitute=True):
        result = self.get(key, from_default, do_substitute)
        return osp.expanduser(result) if result else result

    # TODO: verify that combined custom and default results are properly merged... (only works at end of tree?)
    # noinspection PyProtectedMember
    def _get(self, iter_key, from_default=False):
        """
        load settings using the given key, automatically cascades to default settings if necessary,
        loading default without checking current settings is available via parameter
        :param iter_key: iterable with key parts
        :param from_default: whether to load value from default or 'custom' settings. custom always cascades to default
        """
        if not from_default:
            r = self._data
            if r:
                for arg in iter_key:
                    if isinstance(r, collections.Mapping) and arg in r:
                        r = r[arg]
                    elif isinstance(r, collections.Mapping) and arg not in r:  # and not from_default:
                        return self._fallback._get(iter_key) if self._fallback else None
                    else:
                        return None
                return r
        return self._fallback._get(iter_key) if self._fallback else None

    def put(self, key, value):
        """
        apply a value to a particular key for the currently running configuration
        :param key:
        :param value:
        :return:
        """
        if isinstance(key, string_types):
            target = key.split('/')
        elif isinstance(key, (tuple, list)):
            target = key
        else:
            return None
        return self._put(target, value)

    def _put(self, iter_key, value):
        if self._data is None:
            self._data = dict()
        r = self._data
        l = len(iter_key)
        for i in range(l):
            arg = iter_key[i]
            if i < l - 1 and isinstance(r, collections.Mapping) and arg not in r:  # not at end and missing arg, create missing dict
                r[arg] = dict()
            elif i == l - 1:
                r[arg] = value
                break  # this shouldn't be necessary...
            r = r[arg]
        return value

    def __getitem__(self, item):
        return vpd_get(self, item, do_substitute=True)

    pass


def vpd_data(vpd):
    """
    Shortcut function to return the data (underlying dict/Mapping) from a vpd (VirtualPathDictChain). This was
    used in a few places to quickly grab the underlying dict for serialization and similar purposes.

    :param vpd:
    :return:
    """
    if vpd and isinstance(vpd, VirtualPathDictChain):
        # noinspection PyProtectedMember
        return vpd._data
    elif isinstance(vpd, collections.Mapping):
        return vpd
    return None


class Settings(VirtualPathDictChain):
    settings_file = None

    def __init__(self, data_home, file_name, default_settings_fn):
        """
        Special case of a VirtualPathDictChain used for storing application settings (or similar)

        :param data_home: source path for data / origin path for settings file
        :param file_name: settings yaml file
        :param default_settings_fn: function (lambda?) that provides a dict of default settings (can either be read from
        file, env, hard-coded, or nothing)
        """
        self._dsf = default_settings_fn
        self.data_home = data_home
        self.file_name = file_name
        self.settings_file = osp.join(self.data_home, self.file_name)
        _current_dsf = self._dsf()
        fallback = VirtualPathDictChain(_current_dsf, None) if isinstance(_current_dsf, collections.Mapping) else None
        super(Settings, self).__init__(self._load(), fallback)
        self.refresh()

    # # TODO: evaluate performance implications with or without ttl cache (thread sync vs get look-ups)
    # @ttl_cache(ttl=120)  # TODO: make TTL cache configurable to support unit tests that can check functionality without long waits
    def get(self, key, from_default=False, do_substitute=False):
        return super(Settings, self).get(key, from_default, do_substitute)

    def get_path(self, key, from_default=False, do_substitute=False, **options):
        force_absolute = options.pop('absolute', False)
        relative_origin_coercion = options.pop('relative_origin_coercion', False) or options.pop('roc', False)

        # if relative path, then interpret as relative to origin if `relative_origin_coercion` is True
        path = super(Settings, self).get_path(key, from_default, do_substitute)
        if relative_origin_coercion and not osp.isabs(path):
            path = osp.relpath(path, self.data_home)

        # return either abs or relative path based on `absolute`
        return osp.abspath(path) if force_absolute else path

    def _load(self):
        if osp.exists(self.settings_file):
            with open(self.settings_file, 'rb') as f:
                return yaml.safe_load(f)
        return None

    def commit(self):
        """
        Save current running settings to disk
        """
        raise NotImplementedError()

    def refresh(self):
        """
        discard any changes in memory and refresh configuration to on-disk state
        """
        self.settings_file = osp.join(self.data_home, self.file_name)
        self._data = self._load()
        _current_dsf = self._dsf()
        self._fallback = VirtualPathDictChain(_current_dsf, None) if isinstance(_current_dsf, collections.Mapping) else None
        # TODO: reset TTL cache for get(...)
        return self
