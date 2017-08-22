
import dd.runtime.api


class Qt_py_convert(dd.runtime.api.Context):

    def __init__(self, version=None):
        super(Qt_py_convert, self).__init__(package="qt_py_convert", version=version)

    def setupEnvironment(self):
        self.environ["QT_PY_CONVERT_PACKAGE_ROOT"] = self.package_root
        self.environ["QT_PY_CONVERT_VERSION"] = self.version

        # If there are headers or libraries you want to expose,
        # uncomment, otherwise remove these lines.
        #self.environ["QT_PY_CONVERT_INCLUDE_PATH"] = self.expandPaths("$QT_PY_CONVERT_PACKAGE_ROOT/include")
        #self.environ["QT_PY_CONVERT_LIBRARY_PATH"] = self.expandPaths("$QT_PY_CONVERT_PACKAGE_ROOT/lib")

        # If there are shared libraries, chances are you want to export these.
        #self.environ["LD_LIBRARY_PATH"] = self.expandPaths("$QT_PY_CONVERT_LIBRARY_PATH:$LD_LIBRARY_PATH")

        # If the package contains python code, uncomment this to register
        # the package on the python-path, otherwise remove this line.
        self.environ["PYTHONPATH"] = self.expandPaths("$QT_PY_CONVERT_PACKAGE_ROOT/python:$PYTHONPATH")
        self.environ["PATH"] = self.expandPaths("$QT_PY_CONVERT_PACKAGE_ROOT/bin:$PATH")

        # If the distribution will contain man-pages, uncomment the
        # following line, otherwise, remove it.
        #self.environ["MANPATH"] = self.expandPaths("$QT_PY_CONVERT_PACKAGE_ROOT/share/man:$MANPATH")

        # If the package has a wam workflow registry, add these variables.
        #self.environ['WAM_REGISTRY_PATH'] = self.expandPaths('$QT_PY_CONVERT_PACKAGE_ROOT/wam/registry.xml:$WAM_REGISTRY_PATH')

    def setupLicense(self, license=None):
        """Initialize the environment with the appropriate license 
        informations when applicable.
        """

