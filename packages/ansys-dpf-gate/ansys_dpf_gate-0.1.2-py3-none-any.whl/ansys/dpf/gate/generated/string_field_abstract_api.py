#-------------------------------------------------------------------------------
# StringField
#-------------------------------------------------------------------------------

class StringFieldAbstractAPI:
	@staticmethod
	def init_string_field_environment(object):
		pass

	@staticmethod
	def finish_string_field_environment(object):
		pass

	@staticmethod
	def string_field_delete(field):
		raise NotImplementedError

	@staticmethod
	def string_field_get_entity_data(field, EntityIndex):
		raise NotImplementedError

	@staticmethod
	def string_field_get_number_entities(field):
		raise NotImplementedError

