def pythonize_arg(arg):
    if "[" in arg or "list" in arg.lower():
        return "list"
    elif arg == "QString":
        return "str"
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
