try:
    import __builtin__ as builtins
except ImportError:
    import builtins

def pythonize_arg(arg):
    if arg in dir(builtins):
        return arg
    elif "[" in arg or "list" in arg.lower():
        return "list"
    elif arg == "QString":
        return "str"
    elif arg == "QVariant":
        return "object"
    elif arg.startswith("Q"):
        return arg
    else:
        return "object"


def parse_args(arg_str):
    args = arg_str.split(",")
    _final = []
    for arg in args:
        if not arg:
            continue
        arg_c = arg.strip("&").strip().split(" ")[-1]

        arg_c = pythonize_arg(arg_c)

        _final.append(arg_c)
    final_args = ", ".join(_final)
    return final_args
