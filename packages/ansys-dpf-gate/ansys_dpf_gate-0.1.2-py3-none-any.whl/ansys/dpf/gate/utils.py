import ctypes
import numpy as np
from ansys.dpf.gate.generated import capi
from ansys.dpf.gate import integral_types


def data_processing_core_load_api(path, api_name):
    errorSize = ctypes.c_int(0)
    errorMsg = ctypes.c_wchar_p()
    capi.dll.DataProcessingCore_LoadAPI(str.encode(path), str.encode(api_name), ctypes.byref(errorSize),
                                        ctypes.byref(errorMsg))
    if errorSize.value != 0:
        raise Exception(errorMsg.value)


def to_int32_ptr(to_replace):
    if to_replace is None:
        return None
    elif isinstance(to_replace, np.ndarray):
        return to_replace.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    elif isinstance(to_replace, integral_types.MutableInt32):
        return to_replace.ctypes_pointer()
    elif isinstance(to_replace, integral_types.MutableListInt32):
        return to_replace.val
    elif isinstance(to_replace, (int, np.int)):
        return ctypes.pointer(ctypes.c_int32(to_replace))
    else:
        return (ctypes.c_int32 * len(to_replace))(*to_replace)


def to_int32(to_replace):
    if isinstance(to_replace, int):
        return ctypes.c_int32(to_replace)
    elif isinstance(to_replace, integral_types.MutableInt32):
        return to_replace.val
    else:
        return to_replace


def to_int32_ptr_ptr(to_replace):
    if to_replace is None:
        return None
    elif isinstance(to_replace, np.ndarray):
        return ctypes.pointer(to_replace.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)))
    else:
        return to_replace.ctypes_pointer()


def to_double_ptr(to_replace):
    if to_replace is None:
        return None
    elif isinstance(to_replace, np.ndarray):
        return to_replace.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    elif isinstance(to_replace, integral_types.MutableDouble):
        return to_replace.ctypes_pointer()
    elif isinstance(to_replace, integral_types.MutableListDouble):
        return to_replace.val
    elif isinstance(to_replace, (float, np.float)):
        return ctypes.pointer(ctypes.c_double(to_replace))
    else:
        return (ctypes.c_double * len(to_replace))(*to_replace)


def to_double_ptr_ptr(to_replace):
    if to_replace is None:
        return None
    elif isinstance(to_replace, np.ndarray):
        return ctypes.pointer(to_replace.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    else:
        return to_replace.ctypes_pointer()


def to_char_ptr(to_replace):
    if to_replace is None:
        return None
    if isinstance(to_replace, integral_types.MutableString):
        return to_replace.val
    return ctypes.create_string_buffer(to_replace.encode('utf-8'))


def to_char_ptr_ptr(to_replace):
    if to_replace is None:
        return None
    if isinstance(to_replace, integral_types.MutableListString):
        return ctypes.cast(to_replace.val, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
    elif isinstance(to_replace, integral_types.MutableString):
        return to_replace.cchar_p_p()
    else:
        raise NotImplemented
