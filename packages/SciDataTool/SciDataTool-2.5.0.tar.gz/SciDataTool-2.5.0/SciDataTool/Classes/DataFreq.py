﻿# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/DataFreq.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/SciDataTool/tree/master/SciDataTool/Methods//DataFreq
"""

from os import linesep
from sys import getsizeof
from ._check import set_array, check_var, raise_
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .DataND import DataND

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
try:
    from ..Methods.DataFreq.conv import conv
except ImportError as error:
    conv = error

try:
    from ..Methods.DataFreq.freq_to_time import freq_to_time
except ImportError as error:
    freq_to_time = error

try:
    from ..Methods.DataFreq.sum import sum
except ImportError as error:
    sum = error

try:
    from ..Methods.DataFreq.to_datadual import to_datadual
except ImportError as error:
    to_datadual = error


from numpy import array, array_equal
from numpy import isnan
from ._check import InitUnKnowClassError


class DataFreq(DataND):
    """Class for fields defined in Fourier space"""

    VERSION = 1

    # Check ImportError to remove unnecessary dependencies in unused method
    # cf Methods.DataFreq.conv
    if isinstance(conv, ImportError):
        conv = property(
            fget=lambda x: raise_(
                ImportError("Can't use DataFreq method conv: " + str(conv))
            )
        )
    else:
        conv = conv
    # cf Methods.DataFreq.freq_to_time
    if isinstance(freq_to_time, ImportError):
        freq_to_time = property(
            fget=lambda x: raise_(
                ImportError(
                    "Can't use DataFreq method freq_to_time: " + str(freq_to_time)
                )
            )
        )
    else:
        freq_to_time = freq_to_time
    # cf Methods.DataFreq.sum
    if isinstance(sum, ImportError):
        sum = property(
            fget=lambda x: raise_(
                ImportError("Can't use DataFreq method sum: " + str(sum))
            )
        )
    else:
        sum = sum
    # cf Methods.DataFreq.to_datadual
    if isinstance(to_datadual, ImportError):
        to_datadual = property(
            fget=lambda x: raise_(
                ImportError(
                    "Can't use DataFreq method to_datadual: " + str(to_datadual)
                )
            )
        )
    else:
        to_datadual = to_datadual
    # generic save method is available in all object
    save = save

    def __init__(
        self,
        axes=None,
        FTparameters=-1,
        values=None,
        is_real=True,
        symbol="",
        name="",
        unit="",
        normalizations=-1,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for SciDataTool type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for SciDataTool Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "axes" in list(init_dict.keys()):
                axes = init_dict["axes"]
            if "FTparameters" in list(init_dict.keys()):
                FTparameters = init_dict["FTparameters"]
            if "values" in list(init_dict.keys()):
                values = init_dict["values"]
            if "is_real" in list(init_dict.keys()):
                is_real = init_dict["is_real"]
            if "symbol" in list(init_dict.keys()):
                symbol = init_dict["symbol"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
            if "normalizations" in list(init_dict.keys()):
                normalizations = init_dict["normalizations"]
        # Set the properties (value check and convertion are done in setter)
        # Call DataND init
        super(DataFreq, self).__init__(
            axes=axes,
            FTparameters=FTparameters,
            values=values,
            is_real=is_real,
            symbol=symbol,
            name=name,
            unit=unit,
            normalizations=normalizations,
        )
        # The class is frozen (in DataND init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        DataFreq_str = ""
        # Get the properties inherited from DataND
        DataFreq_str += super(DataFreq, self).__str__()
        return DataFreq_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from DataND
        if not super(DataFreq, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from DataND
        diff_list.extend(
            super(DataFreq, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from DataND
        S += super(DataFreq, self).__sizeof__()
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from DataND
        DataFreq_dict = super(DataFreq, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        DataFreq_dict["__class__"] = "DataFreq"
        return DataFreq_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.axes is None:
            axes_val = None
        else:
            axes_val = list()
            for obj in self.axes:
                axes_val.append(obj.copy())
        if self.FTparameters is None:
            FTparameters_val = None
        else:
            FTparameters_val = self.FTparameters.copy()
        if self.values is None:
            values_val = None
        else:
            values_val = self.values.copy()
        is_real_val = self.is_real
        symbol_val = self.symbol
        name_val = self.name
        unit_val = self.unit
        if self.normalizations is None:
            normalizations_val = None
        else:
            normalizations_val = dict()
            for key, obj in self.normalizations.items():
                normalizations_val[key] = obj.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            axes=axes_val,
            FTparameters=FTparameters_val,
            values=values_val,
            is_real=is_real_val,
            symbol=symbol_val,
            name=name_val,
            unit=unit_val,
            normalizations=normalizations_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except SciDataTool object)"""

        # Set to None the properties inherited from DataND
        super(DataFreq, self)._set_None()
