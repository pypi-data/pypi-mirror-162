# author: Drew Botwinick, Botwinick Innovations
# license: 3-clause BSD
import operator
import re
from functools import reduce

from six import iteritems, string_types

_find_arg_re = re.compile(r"\{(.*?)\}")


# region Argument Interpretation

def arg_substitute(arg, data):
    if isinstance(arg, list):
        return [arg_substitute(a, data) for a in arg]
    elif not isinstance(arg, string_types):
        return None

    def _replace_match(m):
        r = data.get(m.group().strip("}{"))
        return str(r) if r is not None else m.group()  # put back the original if we don't have a match

    return _find_arg_re.sub(_replace_match, arg)


def variable_substitute(arg, data, flatten=False):
    if isinstance(arg, list) and flatten:
        # TODO: switch to chain? maybe just remove flatten altogether?
        return reduce(operator.add, (variable_substitute(a, data, flatten) for a in arg))
    elif isinstance(arg, list):
        return [variable_substitute(a, data, flatten) for a in arg]
    elif not isinstance(arg, string_types):
        return None

    matches = _find_arg_re.findall(arg)
    subs = [data.get(m) for m in matches] if matches else None
    if matches and subs:
        ref_type = type(subs[0])
        types_match = all(type(s) == ref_type for s in subs)
        if types_match and isinstance(subs[0], (list, string_types)):
            if len(subs) > 1:
                return reduce(operator.add, subs)
            else:
                return subs[0]
    return None


def interpret_args_yaml(args, data, default_arg_sep=' ', sub_fn=arg_substitute):
    if args:
        result = []
        for s in args:
            if isinstance(s, dict):
                arg_sep = s.pop('SEPARATOR', default_arg_sep)  # separator between arguments
                key_join = s.pop('KEY_JOIN', default_arg_sep)  # separator between complex arg key and resolved value
                for k, v in iteritems(s):
                    if isinstance(v, list):
                        t = interpret_args_yaml(v, data, default_arg_sep)
                        if t and arg_sep != ' ':
                            t = arg_sep.join(t)
                            if key_join != ' ':
                                result.append(k + key_join + t)
                            else:  # if the separator is ' ' then we're going to pop them on as separate tokens
                                if k:
                                    result.append(k)
                                result.append(t)
                        elif t:
                            result += t  # t is definitely a list at this point...
                    else:
                        t = sub_fn(v, data)
                        if v != t and len(t) > 0:
                            if arg_sep != ' ':
                                result.append(k + arg_sep + t)
                            else:  # if the separator is ' ' then we're going to pop them on as separate tokens
                                if k:
                                    result.append(k)
                                result.append(t)
            else:
                a = sub_fn(s, data)
                if isinstance(a, list):
                    result.extend(a)
                else:
                    result.append(a)
        return result
    return []

# endregion
