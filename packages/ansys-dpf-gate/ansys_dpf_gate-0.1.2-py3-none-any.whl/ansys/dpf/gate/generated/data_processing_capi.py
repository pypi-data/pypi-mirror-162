import ctypes
from ansys.dpf.gate import utils
from ansys.dpf.gate import errors
from ansys.dpf.gate.generated import capi
from ansys.dpf.gate.generated import data_processing_abstract_api

 #-------------------------------------------------------------------------------
# DataProcessing
#-------------------------------------------------------------------------------

class DataProcessingCAPI(data_processing_abstract_api.DataProcessingAbstractAPI):

	@staticmethod
	def data_processing_initialization():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_initialization(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_initialize_with_context(context, dataProcessingCore_xml_path):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.dataProcessing_initializeWithContext(utils.to_int32(context), utils.to_char_ptr(dataProcessingCore_xml_path), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_set_debug_trace(text):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_set_debug_trace(utils.to_char_ptr(text), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_load_library(name, dllPath, symbol):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_load_library(utils.to_char_ptr(name), utils.to_char_ptr(dllPath), utils.to_char_ptr(symbol), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_available_operators():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_available_operators(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_duplicate_object_reference(base):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_duplicate_object_reference(base._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_objects_holds_same_data(a, b):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_objects_holds_same_data(a._internal_obj, b._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_wrap_unknown(data, destructor, type_hash):
		res = capi.dll.DataProcessing_wrap_unknown(data, destructor, type_hash)
		return res

	@staticmethod
	def data_processing_unwrap_unknown(data, expected_type_hash):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_unwrap_unknown(data._internal_obj, expected_type_hash, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_delete_shared_object(data):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_delete_shared_object(data._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_unknown_has_given_hash(data, expected_type_hash):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_unknown_has_given_hash(data._internal_obj, expected_type_hash, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_description_string(data):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_descriptionString(data._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_delete_string(var1):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_deleteString(utils.to_char_ptr(var1), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_string_post_event(output):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_String_post_event(utils.to_char_ptr(output), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_list_operators_as_collection():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_list_operators_as_collection(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_free_ints(data):
		res = capi.dll.DataProcessing_free_ints(utils.to_int32_ptr(data))
		return res

	@staticmethod
	def data_processing_free_doubles(data):
		res = capi.dll.DataProcessing_free_doubles(utils.to_double_ptr(data))
		return res

	@staticmethod
	def data_processing_serialize(obj):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_serialize(obj._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_deserialize(data, dataSize):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_deserialize(utils.to_char_ptr(data), dataSize, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_global_config_as_data_tree():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getGlobalConfigAsDataTree(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_server_version(major, minor):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getServerVersion(ctypes.byref(utils.to_int32(major)), ctypes.byref(utils.to_int32(minor)), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_os():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getOs(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_process_id():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_ProcessId(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_parse_error(size, error_message):
		res = capi.dll.DataProcessing_parse_error(utils.to_int32(size), error_message)
		return res

	@staticmethod
	def data_processing_parse_error_to_str(size, error_message):
		res = capi.dll.DataProcessing_parse_error_to_str(utils.to_int32(size), error_message)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def dpf_error_new():
		res = capi.dll.DpfError_new()
		return res

	@staticmethod
	def dpf_error_set_throw(error, must_throw):
		res = capi.dll.DpfError_set_throw(error, must_throw)
		return res

	@staticmethod
	def dpf_error_set_code(error, code_value):
		res = capi.dll.DpfError_set_code(error, utils.to_int32(code_value))
		return res

	@staticmethod
	def dpf_error_set_message_text(error, code_value):
		res = capi.dll.DpfError_set_message_text(error, utils.to_char_ptr(code_value))
		return res

	@staticmethod
	def dpf_error_set_message_template(error, code_value):
		res = capi.dll.DpfError_set_message_template(error, utils.to_char_ptr(code_value))
		return res

	@staticmethod
	def dpf_error_set_message_id(error, code_value):
		res = capi.dll.DpfError_set_message_id(error, utils.to_char_ptr(code_value))
		return res

	@staticmethod
	def dpf_error_delete(error):
		res = capi.dll.DpfError_delete(error)
		return res

	@staticmethod
	def dpf_error_duplicate(error):
		res = capi.dll.DpfError_duplicate(error)
		return res

	@staticmethod
	def dpf_error_code(error):
		res = capi.dll.DpfError_code(error)
		return res

	@staticmethod
	def dpf_error_to_throw(error):
		res = capi.dll.DpfError_to_throw(error)
		return res

	@staticmethod
	def dpf_error_message_text(error):
		res = capi.dll.DpfError_message_text(error)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def dpf_error_message_template(error):
		res = capi.dll.DpfError_message_template(error)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def dpf_error_message_id(error):
		res = capi.dll.DpfError_message_id(error)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_initialization_on_client(client):
		res = capi.dll.DataProcessing_initialization_on_client(client._internal_obj)
		return res

	@staticmethod
	def data_processing_load_library_on_client(sLibraryKey, sDllPath, sloader_symbol, client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_load_library_on_client(utils.to_char_ptr(sLibraryKey), utils.to_char_ptr(sDllPath), utils.to_char_ptr(sloader_symbol), client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_id_of_duplicate_object_reference(base):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_get_id_of_duplicate_object_reference(base._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_release_obj_by_id_in_db(id, client, bAsync):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_release_obj_by_id_in_db(utils.to_int32(id), client._internal_obj, bAsync, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_parse_error_to_str_for_object(api_to_use, size, error_message):
		res = capi.dll.DataProcessing_parse_error_to_str_for_object(api_to_use._internal_obj, utils.to_int32(size), error_message)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_delete_string_for_object(api_to_use, var1):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_deleteString_for_object(api_to_use._internal_obj, utils.to_char_ptr(var1), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_client(base):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_get_client(base._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_prepare_shutdown(client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_prepare_shutdown(client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_release_server(client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_release_server(client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_string_post_event_for_object(api_to_use, output):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_String_post_event_for_object(api_to_use._internal_obj, utils.to_char_ptr(output), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_free_ints_for_object(api_to_use, data):
		res = capi.dll.DataProcessing_free_ints_for_object(api_to_use._internal_obj, utils.to_int32_ptr(data))
		return res

	@staticmethod
	def data_processing_free_doubles_for_object(api_to_use, data):
		res = capi.dll.DataProcessing_free_doubles_for_object(api_to_use._internal_obj, utils.to_double_ptr(data))
		return res

	@staticmethod
	def data_processing_deserialize_on_client(client, data, dataSize):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_deserialize_on_client(client._internal_obj, utils.to_char_ptr(data), dataSize, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_global_config_as_data_tree_on_client(client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getGlobalConfigAsDataTree_on_client(client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_client_config_as_data_tree():
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getClientConfigAsDataTree(ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_server_version_on_client(client, major, minor):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getServerVersion_on_client(client._internal_obj, ctypes.byref(utils.to_int32(major)), ctypes.byref(utils.to_int32(minor)), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_get_server_ip_and_port(client, port):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getServerIpAndPort(client._internal_obj, ctypes.byref(utils.to_int32(port)), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_get_os_on_client(client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_getOs_on_client(client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_download_file(client, server_file_path, to_client_file_path):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_DownloadFile(client._internal_obj, utils.to_char_ptr(server_file_path), utils.to_char_ptr(to_client_file_path), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_download_files(client, server_file_path, to_client_file_path, specific_extension):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_DownloadFiles(client._internal_obj, utils.to_char_ptr(server_file_path), utils.to_char_ptr(to_client_file_path), utils.to_char_ptr(specific_extension), ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

	@staticmethod
	def data_processing_upload_file(client, file_path, to_server_file_path, use_tmp_dir):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_UploadFile(client._internal_obj, utils.to_char_ptr(file_path), utils.to_char_ptr(to_server_file_path), use_tmp_dir, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		newres = ctypes.cast(res, ctypes.c_char_p).value.decode("utf-8")
		capi.dll.DataProcessing_String_post_event(res, ctypes.byref(errorSize), ctypes.byref(sError))
		return newres

	@staticmethod
	def data_processing_process_id_on_client(client):
		errorSize = ctypes.c_int(0)
		sError = ctypes.c_wchar_p()
		res = capi.dll.DataProcessing_ProcessId_on_client(client._internal_obj, ctypes.byref(utils.to_int32(errorSize)), ctypes.byref(sError))
		if errorSize.value != 0:
			raise errors.DPFServerException(sError.value)
		return res

