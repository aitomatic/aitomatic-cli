import re


def str_to_var(x: str):
    '''
    cleans string to create python safe variable name
    '''
    return re.sub('\W|^(?=\d)', '_', x)


def str_to_value(x: str):
    """
    convert numeric types to numbers and string literals to strings
    """
    undefined = False
    float_fmt = '^\-?\d+\.?\d*$'
    str_literal_fmt = '^\".+\"$'
    if x.startswith('"') and x.endswith('"'):
        # if is string literal
        y = eval(x)
    elif x.isnumeric():
        # if is int
        y = int(x)
    elif re.match(float_fmt, x) is not None:
        # if is float
        y = float(x)
    else:
        # if is undefined variable
        y = x
        undefined = True

    return y, undefined


def get_str_order(vals: list[str]):
    """
    order list so that no earlier item is a substring of a later item
    """
    # sort by length longest to shortest since a longer string cannot be
    # a substring of a shorter string
    result = sorted(vals, key=lambda x: len(x), reverse=True)
    return result
