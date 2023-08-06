#-------------------------------------------------------------------------------
# LabelSpace
#-------------------------------------------------------------------------------

class LabelSpaceAbstractAPI:
	@staticmethod
	def init_label_space_environment(object):
		pass

	@staticmethod
	def finish_label_space_environment(object):
		pass

	@staticmethod
	def label_space_new():
		raise NotImplementedError

	@staticmethod
	def label_space_delete(space):
		raise NotImplementedError

	@staticmethod
	def label_space_add_data(space, label, id):
		raise NotImplementedError

	@staticmethod
	def label_space_set_data(space, label, id):
		raise NotImplementedError

	@staticmethod
	def label_space_erase_data(space, label):
		raise NotImplementedError

	@staticmethod
	def label_space_get_size(space):
		raise NotImplementedError

	@staticmethod
	def label_space_get_labels_value(space, index):
		raise NotImplementedError

	@staticmethod
	def label_space_get_labels_name(space, index):
		raise NotImplementedError

	@staticmethod
	def label_space_has_label(space, label):
		raise NotImplementedError

	@staticmethod
	def label_space_at(space, label):
		raise NotImplementedError

	@staticmethod
	def label_space_new_for_object(api_to_use):
		raise NotImplementedError

