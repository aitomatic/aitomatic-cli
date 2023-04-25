from itertools import product
from copy import deepcopy
from collections import deque


def flatten_dict(x, top=None):
    out = {}
    for k, v in x.items():
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
    for k, v in x.items():
        if k == key:
            out[k] = v
        elif isinstance(k, tuple) and k[0] == key:
            tmp = k[1:]
            if len(tmp) == 0:
                out[k] = v
            else:
                out[tmp] = v

    return out


def search_list(x, key):
    out = []
    for k in x:
        if k == key:
            out.append(k)
        elif isinstance(k, tuple) and k[0] == key:
            tmp = k[1:]
            if len(tmp) == 0:
                out.append(k[0])
            else:
                out.append(tmp)

    return out


def apply_hyperparams_to_dict(params, to_apply):
    tmp_params = deepcopy(params)
    for k, v in params.items():
        subset = search_dict(to_apply, k)
        if len(subset) == 1 and not isinstance(list(subset.keys())[0], tuple):
            tmp_params[k] = list(subset.values())[0]
        elif len(subset) > 0:
            if len(subset) == 1 and list(subset.keys())[0][0] == k:
                tmp_params[k] = list(subset.values())[0]
                continue

            if isinstance(v, dict):
                tmp_params[k] = apply_hyperparams_to_dict(v, subset)
            elif isinstance(v, list):
                tmp_params[k] = [apply_hyperparams_to_dict(x, subset) for x in v]

        else:
            if isinstance(v, dict):
                tmp_params[k] = apply_hyperparams_to_dict(v, to_apply)
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                tmp_params[k] = [apply_hyperparams_to_dict(x, to_apply) for x in v]

    return tmp_params


def drop_params_from_dict(params, to_drop):
    tmp_params = deepcopy(params)
    for k, v in params.items():
        subset = search_list(to_drop, k)
        if len(subset) == 1 and (
            not isinstance(subset[0], tuple) or len(subset[0]) == 1
        ):
            if isinstance(subset[0], tuple):
                drop_key = subset[0][0]
            else:
                drop_key = subset[0]

            if drop_key == k:
                tmp_params.pop(drop_key)
                # tmp_params[drop_key] = {}
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                tmp = deepcopy(v)
                for x in tmp:
                    x.pop(drop_key)
                    # x[drop_key] = {}

                tmp_params[k] = tmp
            elif isinstance(v, dict):
                tmp = deepcopy(v)
                tmp.pop(drop_key)
                # tmp[drop_key] = {}
                tmp_params[k] = tmp

        elif len(subset) > 0:
            ones = [x for x in subset if len(x) == 1]
            rest = [x for x in subset if len(x) > 1]
            for x in ones:
                tmp_params[k].pop(x[0])
                # tmp_params[k][x[0]] = {}

            if isinstance(v, dict):
                tmp_params[k] = drop_params_from_dict(v)
            elif isinstance(v, list):
                tmp_params[k] = [drop_params_from_dict(x, subset) for x in v]
        else:
            if isinstance(v, dict):
                tmp_params[k] = drop_params_from_dict(v, to_drop)
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                tmp_params[k] = [drop_params_from_dict(x, to_drop) for x in v]

    return tmp_params


def generate_train_hyperparams(tuning_range: dict):
    hyperparams = []
    train_keys = tuning_range.keys()

    for params in product(*tuning_range.values()):
        hyperparams.append(dict(zip(train_keys, params)))

    return hyperparams, train_keys
