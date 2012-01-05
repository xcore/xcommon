# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = XC-1

# The APP_NAME variable determines the name of the final .xe file. It should
# not include the .xe postfix. If left blank the name will default to 
# the project name

APP_NAME =

# The flags passed to xcc when building the application
# You can also set the following to override flags for a particular language:
#
#    XCC_XC_FLAGS, XCC_C_FLAGS, XCC_ASM_FLAGS, XCC_CPP_FLAGS
#
# If the variable XCC_MAP_FLAGS is set it overrides the flags passed to 
# xcc for the final link (mapping) stage.

XCC_FLAGS = -O1
XCC_FLAGS_Opt = -O33
XCC_FLAGS_Debug = -g

# The USED_MODULES variable lists other module used by the application. 

USED_MODULES = "module test spacey" "module_test_build" module_test_build_2 "module test spacey 2"

EXCLUDE_FILES = ignore1.xc

XCC_FLAGS_test2.xc = $(XCC_FLAGS) -Os

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.


# Use the main Makefile from module_xmos_common
include ../../xcommon/module_xcommon/build/Makefile.common

