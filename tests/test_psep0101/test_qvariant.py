from qt_py_convert._modules.psep0101 import process
from qt_py_convert.external.redbaron import redbaron
from qt_py_convert.general import AliasDict


def check(source, dest):
    red = redbaron.RedBaron(source)
    process(red, skip_lineno=True, tometh_flag=False)
    convert = red.dumps()
    try:
        assert convert == dest
    except AssertionError as err:
        raise AssertionError("\n%s\n!=\n%s" % (convert, dest))


def test_qvariant_basic():
    check(
        't = QVariant()  # I should become None',
        't = None  # I should become None'
    )


def test_qvariant_list():
    check(
        'tt = QVariant("[23, 19]")  # I should become list',
        'tt = "[23, 19]"  # I should become list'
    )


def test_qvariant_inside_other():
    check(
        'ttt = sum([QVariant("[23, 19]"), 42]) # I should become sum([42, 42])',
        'ttt = sum(["[23, 19]", 42]) # I should become sum([42, 42])'
    )


def test_qvariant_potato():
    check(
        't = QVariant("foo()")',
        't = "foo()"'
    )


def test_qvariant_error_basic():
    s = """if isinstance(
                    value, QVariant
            ):
    pass
"""
    check(
        s,
        s,
    )
    assert len(AliasDict["errors"]) == 1,\
        "There are %d errors, there should be 1" % len(AliasDict["errors"])


if __name__ == "__main__":
    import traceback
    _tests = filter(
        lambda key: True if key.startswith("test_") else False,
        globals().keys()
    )

    failed = []
    for test in _tests:
        try:
            print("Running %s" % test)
            globals()[test]()
            print("    %s succeeded!" % test)
        except AssertionError as err:
            print("    %s failed!" % test)
            failed.append((test, traceback.format_exc()))
        print("")
    for failure_name, failure_error in failed:
        print("""
------------ %s FAILED ------------
%s
""" % (failure_name, failure_error))

    print(
        "\n\n%d failures, %d success, %s%%" % (
            len(failed),
            len(_tests)-len(failed),
            "%.1f" % ((float(len(_tests)-len(failed))/len(_tests))*100)
        )
    )
