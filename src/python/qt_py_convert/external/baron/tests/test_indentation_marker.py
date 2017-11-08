from qt_py_convert.external.redbaron import RedBaron


def test_one():
    source = """
def _getLocalNodeNamesRecurse(node, nameList, nodeType=None):
    if False:
        pass

# 01/22/2014 shwan - I believe this is to create a _new_ layer
class CreateLayerCommand(QtWidgets.QUndoCommand):

    DEFAULT_NAME_TEMPLATE = "layer%d"
    OBJECT_LABEL = "Layer"
    SYNCHRONIZE_CLIENT = True
"""
    RedBaron(source)
