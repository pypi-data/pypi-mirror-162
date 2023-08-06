from ansys.dpf.gate import errors
from ansys.dpf.gate.generated import support_abstract_api

# -------------------------------------------------------------------------------
# Support
# -------------------------------------------------------------------------------


@errors.protect_grpc_class
class SupportGRPCAPI(support_abstract_api.SupportAbstractAPI):

    @staticmethod
    def support_get_as_time_freq_support(support):
        from ansys.grpc.dpf import support_pb2, time_freq_support_pb2
        internal_obj = support.get_ownership()
        if isinstance(internal_obj, time_freq_support_pb2.TimeFreqSupport):
            message = support
        elif isinstance(internal_obj, support_pb2.Support):
            message = time_freq_support_pb2.TimeFreqSupport()
            if isinstance(message.id, int):
                message.id = internal_obj.id
            else:
                message.id.CopyFrom(internal_obj.id)
        else:
            raise NotImplementedError(f"Tried to get {support} as TimeFreqSupport.")
        return message

    @staticmethod
    def support_get_as_meshed_support(support):
        from ansys.grpc.dpf import support_pb2, meshed_region_pb2
        internal_obj = support.get_ownership()
        if isinstance(internal_obj, meshed_region_pb2.MeshedRegion):
            message = support
        elif isinstance(internal_obj, support_pb2.Support):
            message = meshed_region_pb2.MeshedRegion()
            if isinstance(message.id, int):
                message.id = internal_obj.id
            else:
                message.id.CopyFrom(internal_obj.id)
        else:
            raise NotImplementedError(f"Tried to get {internal_obj} as MeshedRegion.")
        return message
