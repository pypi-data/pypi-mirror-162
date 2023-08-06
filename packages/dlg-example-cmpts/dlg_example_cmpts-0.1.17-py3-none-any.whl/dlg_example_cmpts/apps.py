"""
dlg_example_cmpts appComponent module.

This is the module of dlg_example_cmpts containing DALiuGE
application components.
Here you put your main application classes and objects.

Typically a component project will contain multiple components and will
then result in a single EAGLE palette.

Be creative! do whatever you need to do!
"""

__version__ = "0.1.0"
import json
import logging
import os
import pickle
import urllib
from glob import glob

import numpy as np
from dlg import droputils
from dlg.drop import BarrierAppDROP, BranchAppDrop
from dlg.meta import dlg_string_param

logger = logging.getLogger(__name__)

##
# @brief MyBranch
# @details Simple app to demonstrate how to write a branch actually making a
# decision and passing data on.
# Most of the code is boilerplate and can be copied verbatim. Note that a
# branch app is allowed
# to have multiple inputs, but just exactly two outputs. This example is using
# just a single input. There is an associated logical graph available on
# github:
#
#    https://github.com//EAGLE-graph-repo/examples/branchDemo.graph
#
# The application assumes to receive a random floating point array with values
# in the range [0,1] on input. It will calculate the mean of that array and
# then branch depending on whether the mean is smaller or larger than 0.5.
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application class/dlg_example_cmpts.apps.MyBranch/String/ComponentParameter/readonly//False/False/Application class # noqa: E501
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param array Array//Object.Array/InputPort/readwrite//False/False/Port receiving the input array
# @param Y Y//float/OutputPort/readwrite//False/False/English Port carrying the mean value of the array if mean < 0.5
# @param N N//float/OutputPort/readwrite//False/False/English Port carrying the mean value of the array if mean >= 0.5
# @par EAGLE_END


class MyBranch(BranchAppDrop):
    def initialize(self, **kwargs):
        BranchAppDrop.initialize(self, **kwargs)

    def run(self):
        """
        Just reading the input array and calculating the mean.
        """
        input = self.inputs[0]
        data = pickle.loads(droputils.allDropContents(input))
        self.value = data.mean()

    def writeData(self):
        """
        Prepare the data and write to port (self.ind) identified by condition.
        """
        output = self.outputs[self.ind]
        d = pickle.dumps(self.value)
        output.len = len(d)
        logger.info(f">>>>>>> Writing value {self.value} to output {self.ind}")
        output.write(d)

    def condition(self):
        """
        Check value, call write method and return boolean.
        """
        if self.value < 0.5:
            self.ind = 0
            result = True
        else:
            self.ind = 1
            result = False
        self.writeData()
        return result


##
# @brief LengthCheck
#
# This branch returns true if the length of the input array is > 0. It also
# passes the array on to the output ports (will be an empty array in the case
# of N==0).
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application class/dlg_example_cmpts.apps.MyBranch/String/ComponentParameter/readonly//False/False/Application class # noqa: E501
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param array Array//Object.Array/InputPort/readwrite//False/False/Port receiving the input array
# @param Y Y//float/OutputPort/readwrite//False/False/English Port carrying the mean value of the array if mean < 0.5
# @param N N//float/OutputPort/readwrite//False/False/English Port carrying the mean value of the array if mean >= 0.5
# @par EAGLE_END


class LengthCheck(BranchAppDrop):
    def initialize(self, **kwargs):
        BranchAppDrop.initialize(self, **kwargs)

    def readData(self):
        """
        Just reading the inoput array and determining the size
        """
        input = self.inputs[0]
        self.raw = droputils.allDropContents(input)
        data = pickle.loads(self.raw)
        # make sure we always have a ndarray with at least 1dim.
        if isinstance(data, np.ndarray):
            # that's what we want..
            if data.size == 0:
                # fix this strange case
                data = np.array([data])
                self.raw = pickle.dumps(data)
        elif not isinstance(data, np.ndarray) and type(data) not in (
            list,
            tuple,
        ):
            raise TypeError
        else:
            # can only be list or tuple. convert those.
            data = np.array(data)
            self.raw = pickle.dumps(data)

        self.value = data.size

    def writeData(self):
        """
        Write unmodified data to port (self.ind) identified by condition.
        """
        output = self.outputs[self.ind]
        output.len = self.value
        output.write(self.raw)

    def condition(self):
        """
        Check value, call write method and return boolean.
        """
        self.readData()
        if self.value > 0:
            self.ind = 0
            result = True
        else:
            self.ind = 1
            result = False
        self.writeData()
        return result

    def run(self):
        self.readData()


##
# @brief FileGlob
# @details An App that uses glob to find all files matching a
# template given by a filepath and a wildcard string
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application class/dlg_example_cmpts.apps.FileGlob/String/ComponentParameter/readonly//False/False/Application class # noqa: E501
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param wildcard wildcard/"*"/String/InputPort/readwrite//False/False/Port receiving the search pattern
# @param filepath filepath/"."/String/InputPort/readwrite//False/False/Port receiving the path to search
# @param file_list file_list//Object.array/OutputPort/readwrite//False/False/Port carrying the resulting file_list
# @par EAGLE_END


class FileGlob(BarrierAppDROP):
    """
    Simple app collecting file names in a directory
    based on a wild-card pattern
    """

    def initialize(self, **kwargs):
        self.wildcard = self._getArg(kwargs, "wildcard", "*")
        self.filepath = self._getArg(kwargs, "filepath", ".")
        BarrierAppDROP.initialize(self, **kwargs)

    def writeData(self):
        """
        Prepare the data and write to all outputs
        """
        for output in self.outputs:
            d = pickle.dumps(self.value)
            output.len = len(d)
            output.write(d)

    def run(self):
        filetmpl = f"{self.filepath}/{self.wildcard}"
        filetmpl = os.path.expandvars(filetmpl)
        logger.debug(f"Looking for files matching {filetmpl}")
        files = glob(filetmpl)
        self.value = [f for f in files if os.path.isfile(f)]
        if len(self.value) == 0:
            logger.warning(f"No matching files found for {filetmpl}")
        else:
            logger.info(
                f"Number of files found matching {filetmpl}: {len(self.value)}"
            )
        self.writeData()


##
# @brief PickOne
# @details App that picks the first element of an input list, passes that
# to all outputs, except the first one. The first output is used to pass
# the remaining array on. This app is useful for a loop.
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application Class/dlg_example_cmpts.apps.PickOne/String/ComponentParameter/readonly//False/False/Import path for application class
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param rest_array rest_array//Object.array/InputPort/readwrite//False/FalseList of elements
# @param element element//Object.element/OutputPort/readwrite//False/False/Port carrying the first element of input array
# @param rest_array rest_array//Object.array/OutputPort/readwrite//False/False/Port carrying the rest array
# @par EAGLE_END


class PickOne(BarrierAppDROP):
    """
    Simple app picking one element at a time. Good for Loops.
    """

    def initialize(self, **kwargs):
        BarrierAppDROP.initialize(self, **kwargs)

    def readData(self):
        input = self.inputs[0]
        data = pickle.loads(droputils.allDropContents(input))

        # make sure we always have a ndarray with at least 1dim.
        if type(data) not in (list, tuple) and not isinstance(
            data, (np.ndarray)
        ):
            raise TypeError
        if isinstance(data, np.ndarray) and data.ndim == 0:
            data = np.array([data])
        else:
            data = np.array(data)
        value = data[0] if len(data) else None
        rest = data[1:] if len(data) > 1 else np.array([])
        return value, rest

    def writeData(self, value, rest):
        """
        Prepare the data and write to all outputs
        """
        # write rest to array output
        # and value to every other output
        for output in self.outputs:
            if output.name == "rest_array":
                d = pickle.dumps(rest)
                output.len = len(d)
            else:
                d = pickle.dumps(value)
                output.len = len(d)
            output.write(d)

    def run(self):
        value, rest = self.readData()
        self.writeData(value, rest)


##
# @brief ExtractColumn
# @details App that extracts one column of an table-like ndarray. The array is
# assumed to be row major, i.e. the second index refers to columns.
# The column is # selected by index counting from 0. If the array is 1-D the
# result is a 1 element array. The component is passing whatever type is in
# the selected column.
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application Class/dlg_example_cmpts.apps.ExtractColumn/String/ComponentParameter/readonly//False/False/Import path for application class
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param index index/0/Integer/ApplicationArgument/readwrite//False/False/0-base index of column to extract
# @param table_array table_array//array/InputPort/readwrite//False/False/List of elements
# @param column column//Object.1Darray/OutputPort/readwrite//False/False/Port carrying the first element of input array
#               the type is dependent on the list element type.
# @par EAGLE_END
class ExtractColumn(BarrierAppDROP):
    """
    Simple app extracting a column from a 2D ndarray.
    """

    def initialize(self, **kwargs):
        self.index = self._getArg(kwargs, "index", 0)
        BarrierAppDROP.initialize(self, **kwargs)

    def readData(self):
        input = self.inputs[0]
        table_array = pickle.loads(droputils.allDropContents(input))

        # make sure we always have a ndarray with 2dim.
        if not isinstance(table_array, (np.ndarray)) or table_array.ndim != 2:
            raise TypeError
        self.column = table_array[:, self.index]

    def writeData(self):
        """
        Prepare the data and write to all outputs
        """
        # write rest to array output
        # and value to every other output
        for output in self.outputs:
            if output.name == "column":
                d = pickle.dumps(self.column)
                output.len = len(d)
            output.write(d)

    def run(self):
        self.readData()
        self.writeData()


##
# @brief AdvUrlRetrieve
# @details An APP that retrieves the content of a URL and writes
# it to all outputs. The URL can be specified either completely or
# partially through the inputs. In that case the urlTempl parameter can
# use placeholders to construct the final URL.
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application Class/dlg_example_cmpts.apps.AdvUrlRetrieve/String/ComponentParameter/readonly//False/False/Application class
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param urlTempl URL Template/"https://eagle.icrar.org"/String/ApplicationArgument/readwrite//False/False/The URL to retrieve
# @param urlPart URL Part//String/InputPort/readwrite//False/False/The port carrying the content read from the URL.
# @param content Content//String/OutputPort/readwrite//False/False/The port carrying the content read from the URL.
# @par EAGLE_END
class AdvUrlRetrieve(BarrierAppDROP):
    """
    An App that retrieves the content of a URL and allows to construct the URL
    through input placeholders.

    Keywords:
    URL:   string, URL to retrieve.
    """

    def initialize(self, **kwargs):
        self.urlTempl = self._getArg(kwargs, "urlTempl", "")
        BarrierAppDROP.initialize(self, **kwargs)

    def constructUrl(self):
        url = self.urlTempl
        # this will ignore inputs not referenced in template
        for x, v in enumerate(self.urlParts):
            pathRef = "%%i%d" % (x,)
            if pathRef in url:
                url = url.replace(pathRef, v)
        logger.info(f"Constructed URL: {url}")
        return url

    def readData(self):
        # for this app we are expecting URL fractions on the inputs
        urlParts = []
        for input in self.inputs:
            part = pickle.loads(droputils.allDropContents(input))
            # make sure the placeholders are strings
            logger.info(f"URL part: {part}")
            if not isinstance(part, str):
                raise TypeError
            urlParts.append(part)
        self.urlParts = urlParts
        self.url = self.constructUrl()
        try:
            u = urllib.request.urlopen(self.url)
        except Exception as e:
            raise e
        # finally read the content of the URL
        self.content = u.read()

    def writeData(self):
        """
        Prepare the data and write to all outputs
        """
        outs = self.outputs
        written = False
        if len(outs) < 1:
            raise Exception("At least one output required for %r" % self)
        for output in outs:
            if output.name.lower() == "content":
                # we are not pickling here, but just pass on the data.
                output.len = len(self.content)
                output.write(self.content)
                written = True
            else:
                logger.warning(f"Output with name {output.name} ignored!")

        if not written:
            raise TypeError(
                "No matching output drop found." + "Nothing written"
            )

    def run(self):
        self.readData()
        self.writeData()


##
# @brief String2JSON
# @details App that reads a string from a single input and tries
# to convert that to JSON. If port is converted into an argument the
# JSON value is taken from there.
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application Class/dlg_example_cmpts.apps.String2JSON/String/ComponentParameter/readonly//False/False/Application class
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param string string//String/InputPort/readwrite//False/False/String to be converted
# @param element element//Object.json/OutputPort/readwrite//False/False/Port carrying the JSON structure
# @par EAGLE_END
class String2JSON(BarrierAppDROP):

    arg: str = dlg_string_param("string", None)

    def initialize(self, **kwargs):
        BarrierAppDROP.initialize(self, **kwargs)
        if not self.arg:
            self.arg = self._getArg(kwargs, "string", None)

    def readData(self):
        input = self.inputs[0]  # ignore all but the first
        try:
            data = json.loads(droputils.allDropContents(input))
        except json.decoder.JSONDecodeError:
            raise TypeError
        return data

    def writeData(self, data):
        """
        Prepare the data and write to all outputs
        """
        # write rest to array output
        # and value to every other output
        for output in self.outputs:
            d = pickle.dumps(data)
            output.len = len(d)
            output.write(d)

    def run(self):
        if (
            len(self.inputs) == 0
        ):  # if there is no input use the argument value
            try:
                logger.debug("Input found: %s", self.arg)
                data = json.loads(self.arg)
            except TypeError:
                raise
        else:
            data = self.readData()
        self.writeData(data)
        del data  # make sure this is cleaned up


##
# @brief GenericGather
# @details App that reads all its inputs and simply writes them in
# concatenated to all its outputs. This can be used stand-alone or
# as part of a Gather. It does not do anything to the data, just
# passing it on.
#
# @par EAGLE_START
# @param category PythonApp
# @param appclass Application Class/dlg_example_cmpts.apps.GenericGather/String/ComponentParameter/readonly//False/False/Import path for application class
# @param execution_time Execution Time/5/Float/ComponentParameter/readonly//False/False/Estimated execution time # noqa: E501
# @param num_cpus No. of CPUs/1/Integer/ComponentParameter/readonly//False/False/Number of cores used # noqa: E501
# @param input input//Object/InputPort/readwrite//False/False/0-base placeholder port for inputs
# @param output output//Object/OutputPort/readwrite//False/False/Placeholder port for outputs
# @par EAGLE_END
class GenericGather(BarrierAppDROP):
    def initialize(self, **kwargs):
        BarrierAppDROP.initialize(self, **kwargs)

    def readWriteData(self):

        inputs = self.inputs
        outputs = self.outputs
        total_len = 0
        for input in inputs:
            total_len += input.len
        for output in outputs:
            output.len = total_len
            for input in inputs:
                d = droputils.allDropContents(input)
                output.write(d)

    def run(self):
        self.readWriteData()
