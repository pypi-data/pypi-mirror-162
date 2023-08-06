from ansys.dpf.gate.generated import label_space_abstract_api

#-------------------------------------------------------------------------------
# LabelSpace
#-------------------------------------------------------------------------------

class LabelSpaceGRPCAPI(label_space_abstract_api.LabelSpaceAbstractAPI):

    @staticmethod
    def label_space_new_for_object(object):
        from ansys.grpc.dpf import collection_pb2
        return collection_pb2.LabelSpace()

    @staticmethod
    def label_space_add_data(space, label, id):
        space._internal_obj.label_space[label] = id
