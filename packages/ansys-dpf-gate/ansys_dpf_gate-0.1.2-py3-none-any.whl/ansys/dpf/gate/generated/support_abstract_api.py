#-------------------------------------------------------------------------------
# Support
#-------------------------------------------------------------------------------

class SupportAbstractAPI:
	@staticmethod
	def init_support_environment(object):
		pass

	@staticmethod
	def finish_support_environment(object):
		pass

	@staticmethod
	def support_delete(support):
		raise NotImplementedError

	@staticmethod
	def support_is_domain_mesh_support(support):
		raise NotImplementedError

	@staticmethod
	def support_set_as_domain_mesh_support(support, meshed_region):
		raise NotImplementedError

	@staticmethod
	def support_get_as_meshed_support(support):
		raise NotImplementedError

	@staticmethod
	def support_get_as_cyclic_support(support):
		raise NotImplementedError

	@staticmethod
	def support_get_as_time_freq_support(support):
		raise NotImplementedError

