import copy
import numpy as np
from ansys.dpf.gate.generated import dpf_vector_capi
from ansys.dpf.gate.integral_types import MutableListInt32, MutableInt32, MutableListDouble


class DPFVectorBase:
    """
    Base class of DPF vector.
    In the init, creates an instance of DPFVector in the client CLayer.
    The class make thr usage of CAPI calls more friendly by wrapping ctypes and setting
    parameters by reference possible.

    Parameters
    ----------
    client: object having _internal_obj attribute and a shared CLayer Client instance, optional
        Enables DPFClientAPI to choose the right API to use.

    api: DpfVectorAbstractAPI, optional
    """

    def __init__(self, client, api):
        self.dpf_vector_api = api
        self._modified = False
        self._check_changes = True
        try:
            if not client:
                self._internal_obj = self.dpf_vector_api.dpf_vector_new()
                self._check_changes = False
            else:
                self._internal_obj = self.dpf_vector_api.dpf_vector_new_for_object(client)
        except AttributeError:
            raise NotImplementedError

    @property
    def internal_size(self) -> MutableInt32:
        """
        Returns
        -------
        size: MutableInt32
            Custom int object which can be changed by reference.
        """
        return self._array.internal_size

    def start_checking_modification(self) -> None:
        """
        Takes a deep copy of the current data as a numpy array
        in self._initial_data, if self._check_changes is set to True.
        In that case, at deletion, the current data is compared to the initial one
        and the data is updated server side if it has changed.

        Notes
        -----
        self._check_changes is set to True by default when a client is added at the class init

        """
        if self._check_changes:
            self._initial_data = copy.deepcopy(self.np_array)

    def has_changed(self):
        """
        If self._check_changes is set to True, compares the initial data computed in
        ```start_checking_modification``` to the current one.

        Notes
        -----
        self._check_changes is set to True by default when a client is added at the class init
        """
        if self._check_changes:
            if self._modified or not np.allclose(self._initial_data, self.np_array):
                self._modified = True
        return self._modified


    @property
    def np_array(self) -> np.ndarray:
        """
        Returns
        -------
        numpy.ndarray
            numpy array to the internal data (with no data copy)

        Warnings
        --------
        Memory of the DPFVector is not managed in this object. Use a ```DPFArray``` instead.
        """
        if not self._array.pointer or self.size==0:
            return np.empty((0,), dtype=np.dtype(self._array.pointer._type_))
        return np.ctypeslib.as_array(self._array.pointer, shape=(self.size,))

    @property
    def size(self) -> int:
        """Size of the data array (returns a copy)"""
        return int(self.internal_size)

    def start_checking_modification(self) -> None:
        """
        Takes a deep copy of the current data as a numpy array
        in self._initial_data, if self._check_changes is set to True.
        In that case, at deletion, the current data is compared to the initial one
        and the data is updated server side if it has changed.

        Notes
        -----
        self._check_changes is set to True by default when a client is added at the class init

        """
        if self._check_changes:
            self._initial_data = copy.deepcopy(self.np_array)

    def has_changed(self):
        """
        If self._check_changes is set to True, compares the initial data computed in
        ```start_checking_modification``` to the current one.

        Notes
        -----
        self._check_changes is set to True by default when a client is added at the class init
        """
        if self._check_changes:
            if self._modified or not np.allclose(self._initial_data, self.np_array):
                self._modified = True
        return self._modified

    def __del__(self):
        try:
            self.dpf_vector_api.dpf_vector_delete(self)
        except:
            pass


class DPFVectorInt(DPFVectorBase):
    def __init__(self, client=None, api=dpf_vector_capi.DpfVectorCAPI):
        super().__init__(client, api)
        self._array = MutableListInt32()

    @property
    def internal_data(self) -> MutableListInt32:
        """
        Returns
        -------
        internal_data: MutableListInt32
            Custom int list object which can be changed by reference and which is compatible with ctypes
        """
        return self._array

    def commit(self) -> None:
        """Updates the data server side when necessary:
        if self._check_changes is set to True, compares the initial data computed in
        ```start_checking_modification``` (which should have been called beforehand) to the current one.
        """
        self.dpf_vector_api.dpf_vector_int_commit(self, self.internal_data, self.internal_size, self.has_changed())

    def __del__(self):
        try:
            if self._array:
                self.dpf_vector_api.dpf_vector_int_free(self, self.internal_data, self.internal_size, self.has_changed())
        except:
            pass
        super().__del__()


class DPFVectorDouble(DPFVectorBase):
    def __init__(self, client=None, api=dpf_vector_capi.DpfVectorCAPI):
        super().__init__(client, api)
        self._array = MutableListDouble()

    @property
    def internal_data(self) -> MutableListDouble:
        """
        Returns
        -------
        internal_data: MutableListDouble
            Custom double list object which can be changed by reference and which is compatible with ctypes
        """
        return self._array

    def commit(self) -> None:
        """Updates the data server side when necessary:
        if self._check_changes is set to True, compares the initial data computed in
        ```start_checking_modification``` (which should have been called beforehand) to the current one.
        """
        self.dpf_vector_api.dpf_vector_double_commit(self, self.internal_data, self.internal_size, self.has_changed())

    def __del__(self):
        try:
            if self._array:
                self.dpf_vector_api.dpf_vector_double_free(self, self.internal_data, self.internal_size, self.has_changed())
        except:
            pass
        super().__del__()
