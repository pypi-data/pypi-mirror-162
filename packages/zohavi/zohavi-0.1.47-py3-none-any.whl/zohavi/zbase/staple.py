import inspect, json

class ZStaple:
	def __init__(self, app=None, logger=None):
		self.logger = logger
		self.app = app
		self.debug = False

	def get_callee_str(self):
		callee = inspect.stack()[2]
		callee_file = callee.filename[ callee.filename.rfind('/'): ]

		ret_str = f"{callee_file }:{callee.lineno}:{callee.function}:" 
		# breakpoint()
		return ret_str

	def log_debug(self, message): 
		if self.logger: self.logger.debug( message, stack_level=2)
		else: print( "DEBUG:" + message )

	def log_error(self, message):
		if self.logger: self.logger.error( message, stack_level=2)
		else: print( "ERROR:" + message )

	def log_info(self, message):
		if self.logger: self.logger.info( message, stack_level=2)
		else: print( "INFO:" + message )

	def log_warning(self, message):
		if self.logger: self.logger.warning( message, stack_level=2)
		else: print( "WARNING:" + message )
