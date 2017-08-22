
# The version of the package Makefile.
USE_MAKEFILE_VERSION = 3
 
# List of sub-directories where there are Makefiles to invoke.
# By default SRC_DIR will be recursively searched.
#COMPILE_DIRS += $(SRC_DIR)/maya/plugins
 
# List of wrapper scripts to install when invoking the target `wrapper'.
# By default, all files under $PACKAGE_ROOT/wrappers will be installed.
#WRAPPERS += src/wrappers/qt_py_convert
 
# List of platform names to install distributions and wrappers on.
# By default, installation will always be performed for the current platform.
#PLATFORMS ?= cent6_64
 
# Type of documentation to generate for this package. The default is 'html'.
#DOCS += html
#DOCS += man
 
# List of user targets to invoke after a successful build.
#BUILD_POST_TARGETS += build-post
 
# Standard facility Makefile, must be included after configuration.
include $(DD_TOOLS_ROOT)/etc/Makefile.tdpackage
 
# ====
# User-rules go here...
#
#.PHONY: build-post
#build-post:
#   do something here