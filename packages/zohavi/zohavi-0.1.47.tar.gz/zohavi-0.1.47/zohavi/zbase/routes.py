import json
from pathlib import Path
  
from flask_classful import  FlaskView,  route 
from . import bp

from flask_login import current_user #,   login_required
from flask_classful import FlaskView, route
from flask import   send_file, current_app, render_template,  current_app , abort, jsonify

from .staple import ZStaple
 


class BaseView(FlaskView, ZStaple):
	route_base = '/'
	# bpname = 'base'
	bp = bp

	##############################################################################################################
	def __init__(self):
		self.module_name = __name__ 

	##############################################################################################################
	def register_app(self, app_ref, logger_ref):
		self.myapp = app_ref
		self.logger = logger_ref

	# def log_debug(self, message):
	# 	if self.logger: self.logger.debug( message )
	# 	else: print( "DEBUG:" + message )

	# def log_error(self, message):
	# 	if self.logger: self.logger.error( message )
	# 	else: print( "ERROR:" + message )

	# def log_info(self, message):
	# 	if self.logger: self.logger.info( message )
	# 	else: print( "INFO:" + message )

	# def log_warning(self, message):
	# 	if self.logger: self.logger.warning( message )
	# 	else: print( "WARNING:" + message )


	##############################################################################################################
	#	list all routes
	##############################################################################################################
	@route("/routes", methods=["GET"])
	def getRoutes(self):
		routes = {}
		for rule_item in current_app.url_map._rules:
			routes[rule_item.rule] = {}
			routes[rule_item.rule]["functionName"] = rule_item.endpoint
			routes[rule_item.rule]["methods"] = list(rule_item.methods)

		# routes.pop("/static/<path:filename>")

		return jsonify(routes)


	# @self.myapp.app.after_request
	# def set_response_headers(response):
	# 	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	# 	response.headers['Pragma'] = 'no-cache'
	# 	response.headers['Expires'] = '0'
	# 	return response

	##############################################################################################################
	#	Return any static resources
	##############################################################################################################
	@route('/st/<string:subdir_type>/<string:module>/<path:resourceFile>')
	def get_page(self, subdir_type, module, resourceFile):		
		# path = current_app.config['APP_BASE_DIR']
		path = current_app.config['ENV_BASE_DIR']
		if subdir_type in [ "_def", "app"]: 
			path += subdir_type + "/" 
		else:
			logger.error( f"incorrect type sent of:{subdir_type}")
			abort(500)

		send_file_path = path + module + "/" + resourceFile

 
		if Path(send_file_path).is_file():
			logger.debug("file found:" + str(send_file_path)   )
			return send_file(send_file_path)

		logger.error("file missing:" + str(send_file_path)   )
		abort(404)

