"""
dlg_example_cmpts component module.

This is the module of daliuge_component_examples containing DALiuGE data
components. Here you put your main data classes and objects.

Typically a component project will contain multiple components and will
then result in a single EAGLE palette.

Be creative! do whatever you need to do!
"""
import logging

from dlg.drop import AbstractDROP

logger = logging.getLogger(__name__)

##
# @brief MyData
# @details Template app for demonstration only!
# Replace the documentation with whatever you want/need to show in the DALiuGE
# workflow editor. The dataclass parameter should contain the relative
# Pythonpath to import MyApp.
#
# @par EAGLE_START
# @param category File
# @param appclass DropClass/dlg_example_cmpts.MyData/String/ComponentParameter/readonly//False/False/Import direction for application class
# @param dummy Dummy parameter/ /String/ApplicationArgument/readwrite//False/False/Dummy modifyable parameter
# @param dummy Dummy in//float/InputPort/readwrite//False/False/Dummy producer port
# @param dummy Dummy out//float/OutputPort/readwrite//False/False/Dummy consumer port
# @par EAGLE_END

# Data components usually directly inhert from the AbstractDROP class. Please
# refer to the Developer Guide for more information.


class MyDataDROP(AbstractDROP):
    """
    A dummy dataDROP that points to nothing.
    """

    def initialize(self, **kwargs):
        pass

    def getIO(self):
        return f"Hello from {__class__.__name__}"

    @property
    def dataURL(self):
        return "Hello from the dataURL method"
