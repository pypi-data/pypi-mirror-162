from collections.abc import Iterable, Mapping


def wrap_list(some):
    if isiter(some, allow_dict=False):
        return some
    return [some]


def isiter(arg, allow_dict=True, allow_str=False):
    if not isinstance(arg, Iterable):
        return False
    elif type(arg) is str and not allow_str:
        return False
    elif type(arg) is dict and not allow_dict:
        return False
    else:
        return True


def chunk_iter(iterable, size):
    arr = []
    for some in iterable:
        arr.append(some)
        if len(arr) >= size:
            yield arr
            arr = []
    if len(arr) > 0:
        yield arr


def deep_update(source, d):
    for k, v in d.items():
        if isinstance(v, Mapping):
            source[k] = deep_update(source.get(k, {}), v)
        else:
            source[k] = v
    return source
