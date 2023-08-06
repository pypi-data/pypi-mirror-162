#IMPORT STANDARD
import os, sys , re
 
from flask import Flask, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 

import pymongo
from zohavi.zwebui.jinja_cust_funcs import JCFunc
from zohavi.zconfig.models import MDL_Config
	
class AppCore:
	def __init__(self, app,  sccfg, env, test_only=False): 
		self._app = app 
		# self._app.config.update( config.to_flask()  )

		self._app.config['SQLALCHEMY_DATABASE_URI'] = sccfg.get_env_config( env ).db_core
		self.db = SQLAlchemy(self._app)
		self._ref_config = MDL_Config( logger=None, db=self.db)

		if not test_only: 
			self._sync_core_config_to_db( sccfg, env )
			self._app.config.update( self._ref_config.to_flask_config()  )

		# self.db = SQLAlchemy(self._app)
		self._migrate = Migrate(self._app, self.db)


		self.login = LoginManager(self._app)
		self.login.login_message_category = "danger"  #when cannot login, set error type to red color on display
		self.login.login_view = 'user.login'		#The function name in routes that will handle the login page 

		# self._mongodb = pymongo.MongoClient(   self.get_config( "MONGODB_URL" ) ) #"mongodb://localhost:27017/"

		self._set_custom_template_loaders()
		self._define_template_funcions( self._app.jinja_env )

	def run(self, *args, **kwargs):
		self._app.run(*args, **kwargs)

	##############################################################################################
	# Copy the basic cofig and put it to the database
	def _sync_core_config_to_db(self,  sccfg, env):
		self._ref_config.set_config( config_str='SYS///LOG_FILE', value=sccfg.get_env_config( env ).log_file )
		self._ref_config.set_config( config_str='SYS///HOST', value=sccfg.get_env_config( env ).host )
		self._ref_config.set_config( config_str='SYS///PORT', value=sccfg.get_env_config( env ).port )
		self._ref_config.set_config( config_str='SYS/DIR//BASE_DIR', value=sccfg.get_env_config( env ).base_dir )
		self._ref_config.set_config( config_str='SYS/DB//CORE', value=sccfg.get_env_config( env ).db_core )


	##############################################################################################
	def get_config(self, config_str):
		# breakpoint()
		return self._ref_config.get_config( config_str=config_str)

	################################################################################################
	# Add reference to the main logger
	def register_logger(self, logger):
		self._logger = logger

	# ################################################################################################
	# # Commit to the database with an exception 
	# def safe_add_and_commit(self, obj ):
	# 	self.db.session.add(obj)
	# 	return self.safe_commit(obj )

	# ################################################################################################
	# # Commit to the database with an exception 
	# def safe_commit(self, obj=None ):
	# 	try:
	# 		self.db.session.commit()
	# 		if obj: 
	# 			self.db.session.refresh(obj) 
	# 			return obj
	# 	except Exception as error:
	# 		self._logger.error("DB Error:" + str(error)  )
	# 	return True
		 
	##############################################################################################################
	def _set_custom_template_loaders(self):
		from jinja2 import ChoiceLoader, FileSystemLoader

		if 'CUST_TEMPLATE_OVERRIDEDIR' in self._app.config:
			my_loader = ChoiceLoader([ FileSystemLoader(self._app.config['CUST_TEMPLATE_OVERRIDEDIR']) ])
			self._app.jinja_loader = my_loader

	##############################################################################################################
	def _define_template_funcions(self, jinja_env):
		for method in dir(JCFunc):
			if method.startswith('__') is False:
				jinja_env.globals[ 'jc_' + method] = getattr(JCFunc, method)
		 
	##############################################################################################################
	def setup_blueprint_dyn( self, bp_module_class_str ,  route_module_class_str =None,  url_prefix =None  ):

		#import the module that contains the FlaskView class
		bp_tokens = bp_module_class_str.split('#')
		if len(bp_tokens) != 2: raise Exception('Must pass module#class_name - e.g. app.siteadmin.routes#SiteAdminView')
		bp_module = __import__( bp_tokens[0] , globals(), locals(), [ bp_tokens[1] ] ) 
		bp_class =  getattr(bp_module, bp_tokens[1] )

		#call the register function from the FlaskView class to ensure the routes are registered
		if route_module_class_str: 
			route_tokens = route_module_class_str.split('#')
			if len(route_tokens) != 2: raise Exception('Must pass module#class_name - e.g. app.siteadmin.routes#SiteAdminView')
			route_module = __import__( route_tokens[0] , globals(), locals(), [ route_tokens[1] ] )  
			route_class = getattr( route_module, route_tokens[1] )
			# breakpoint()
			route_class.register(  bp_class  )	

		# if local_templates: blueprint.bp.jinja_loader.searchpath.append( local_templates )
		

		self._app.register_blueprint( bp_class , url_prefix= url_prefix   )

		# return blueprint.bp
