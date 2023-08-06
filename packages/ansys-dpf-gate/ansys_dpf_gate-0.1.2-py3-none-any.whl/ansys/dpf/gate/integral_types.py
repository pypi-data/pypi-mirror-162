import ctypes

class MutableInt32:
    def __init__(self, val=0):
        self.set(val)

    def ctypes_pointer(self):
        return ctypes.pointer(self.val)

    def set(self, val):
        self.val = ctypes.c_int32(val)

    def __int__(self):
        return self.val.value


class MutableListInt32:
    def __init__(self, size=0):
        self.val = ctypes.pointer(ctypes.c_int32(0))
        self._size = MutableInt32(size)
        if size != 0:
            tmp = list(range(size))
            self.val = (ctypes.c_int32 * len(tmp))(*tmp)

    def ctypes_pointer(self):
        return ctypes.pointer(self.val)

    @property
    def pointer(self):
        return self.val

    @property
    def internal_size(self):
        return self._size

    def tolist(self):
        if isinstance(self.val, list):
            return self.val
        return [int(self.val[i]) for i in range(0, int(self._size))]

    def set(self, val: list):
        self.val = val
        self._size = len(val)


class MutableDouble:
    def __init__(self, val=0.):
        self.set(val)

    def ctypes_pointer(self):
        return ctypes.pointer(self.val)

    def set(self, val):
        self.val = ctypes.c_double(val)

    def __float__(self):
        return self.val.value


class MutableListDouble:
    def __init__(self):
        self.val = ctypes.pointer(ctypes.c_double(0))
        self._size = MutableInt32(0)

    def ctypes_pointer(self):
        return ctypes.pointer(self.val)

    @property
    def pointer(self):
        return self.val

    @property
    def internal_size(self):
        return self._size

    def tolist(self):
        if isinstance(self.val, list):
            return self.val
        return [float(self.val[i]) for i in range(0, int(self._size))]

    def set(self, val: list):
        self.val = val
        self._size = len(val)


class MutableString:
    def __init__(self, size):
        self.val = ctypes.create_string_buffer(size)

    def set_str(self, value_str):
        self.val = value_str

    def set(self, value_str):
        self.val = value_str

    def cchar_p_p(self):
        self.val = ctypes.c_char_p()
        self.val_p = ctypes.byref(self.val)
        return  ctypes.cast(self.val_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))

    def __str__(self):
        if hasattr(self.val, "value"):
            return self.val.value.decode("utf8")
        return str(self.val)


class MutableListString:
    def __init__(self, list):
        self.val = (ctypes.c_char_p * len(list))()
        self.val[:] = [s.encode("utf8") for s in list]

    def tolist(self):
        if isinstance(self.val, list):
            return self.val
        return [val.decode("utf8") for val in self.val]