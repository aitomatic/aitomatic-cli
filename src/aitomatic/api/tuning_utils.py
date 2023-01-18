from copy import deepcopy
from collections import deque

def flatten_dict(x, top=None):
    out = {}
    for k,v in x.items():
        if top is not None:
            key = top.copy()
            key.append(k)
        else:
            key = deque([k])

        if isinstance(v, dict):
            tmp = flatten_dict(v, top=key)
            out.update(tmp)
            continue
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            for i, y in enumerate(v):
                tmp_key = key.copy()
                tmp_key.append(i)
                tmp = flatten_dict(y, top=tmp_key)
                out.update(tmp)

            continue

        out[tuple(key)] = v

    return out

def search_dict(x, key):
    out = {}
    for k,v in x.items():
        if k == key:
            out[k] = v
        elif isinstance(k, tuple) and k[0] == key:
            tmp = k[1:]
            if len(tmp) == 0:
                out[k] = v
            else:
                out[k[1:]] = v

    return out

def apply_hyperparams_to_dict(params, to_apply):
    tmp_params = deepcopy(params)
    for k,v in params.items():
        subset = search_dict(to_apply, k)
        if len(subset) == 1 and (not isinstance(list(subset.keys())[0], tuple)
                                 or len(list(subset.keys())[0])):
            print(f'{k}: found value in to_appy: {subset}')
            tmp_params[k] = list(subset.values())[0]
        elif len(subset) > 0:
            print(f'{k}: diving down {subset}')
            if isinstance(v, dict):
                tmp_params[k] = apply_hyperparams_to_dict(v, subset)
            elif isinstance(v, list):
                tmp_params[k] = [apply_hyperparams_to_dict(x, subset) for x in v]
        else:
            if isinstance(v, dict):
                print(f'{k}: continuing')
                tmp_params[k] = apply_hyperparams_to_dict(v, to_apply)
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                print(f'{k}: listing')
                tmp_params[k] = [apply_hyperparams_to_dict(x, to_apply)
                                 for x in v]
            else:
                print(f'{k}: passing')

    return tmp_params
