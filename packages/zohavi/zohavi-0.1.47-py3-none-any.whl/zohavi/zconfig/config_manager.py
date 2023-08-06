import os, sys, ast
from dataclasses import dataclass, field
from typing import List, Dict 


import jsoncfg

from prepost import PreCond
from jsondbupload import JsonDBUpload

@dataclass
class CoreConfigItem():

	@property
	def log_full_path(self) -> str:
		return self.log_file.replace( "!", self.base_dir)

	env:str
	host: str
	port: int
	db_core: str 
	base_dir: str
	log_file: str
	log_full_path: str= field(init=False, default=log_full_path)


class CoreConfig():
	@PreCond.minimum_not_null(2)
	def __init__(self, filename:str=None, config_str:str=None, base_dir:str=None):
		self.env_config = {}

		if filename: config = config = jsoncfg.load_config( filename )
		elif config_str: config = config = jsoncfg.loads_config( config_str )
		self._extract_values( config , base_dir)

	def _extract_values(self, config_raw_data_dict, base_dir:str):
		# breakpoint()
		for config_env in config_raw_data_dict().keys():
			data_dict = {}
			# for config_item in config_env['config_list']:
			data_dict['env'] = config_env

			env_data = config_raw_data_dict[ config_env ]()
			for field  in env_data.keys():
				data_dict[ field ] = env_data[ field ]

			data_dict['base_dir'] = base_dir
			scc_item = CoreConfigItem( **data_dict ) 
			self.env_config[ config_env ] = scc_item
			# print(scc_item)

	def get_env_config(self, env) -> CoreConfigItem:
		return self.env_config[ env ] 




############################################################
############################################################
############################################################
############################################################
class ConfigLoaderFunc():
	@staticmethod
	def append_to_env_field(cfg, raw_param):
		param = ast.literal_eval(raw_param) 
		return ConfigLoaderFunc().get_env_field(cfg, raw_param) + param['suffix'] 

	@staticmethod
	def get_env_field(cfg, raw_param):
		param = ast.literal_eval(raw_param) 
		curr_config = cfg.get_env_config( param['key_path']) #[0], param['key'][1], param['key'][2], param['key'][3]  )
		return curr_config 

	@staticmethod
	def get_working_dir(cfg,  raw_param):
		curr_dir = os.path.dirname( os.path.abspath(sys.argv[0]) )
		return curr_dir + '/'		

	@staticmethod
	def get_random_key(cfg,   raw_param):
		return os.urandom(32)

	@staticmethod
	def load_config( cfg, raw_param):
		path = ConfigLoaderFunc().append_to_env_field(cfg, raw_param)
		print( f"***checking {path}")
		config = jsoncfg.load_config(path)()

		param = ast.literal_eval(raw_param) 
		# breakpoint()
		if 'load_sub_path' in param:
			for token in param['load_sub_path'].split('/'):
				config = config[token]
		# breakpoint()
		return config

# ############################################################
# class ConfigManager():
# 	def __init__(self, session, logger):
# 		self.session = session
# 		self.logger = logger

# 		self.J2DB = JsonDBUpload( session, logger)
# 		# pass

# 	#####################################################################################
# 	#	Save the config data to database
# 	def save_defaults(self, config_defaults_file):
# 		self.J2DB.update_tables_from_file( config_defaults_file )
# 		# pass

# 	#####################################################################################
# 	#	Read the config data
# 	def load(self):
# 		pass

# 	def get(self, area=None, category=None, sub_cat=None, name=None, default=None):
# 		pass

# ############################################################
# class ConfigCoreLoader():
# 	@PreCond.minimum_not_null(1)
# 	def __init__(self, filename=None, data_str = None):
# 		if filename: self._config = jsoncfg.load_config( filename)
# 		elif data_str: self._config = jsoncfg.loads_config( data_str )
	
# 	def get_config(self):
# 		return self._config
# 	def get_config_env(self, env, config_item):
# 		return self._config[env][config_item].value

############################################################
class ConfigTemplate():
	CFG = {} 
	env_code = "def"

	############################################################
	def __init__(self, env_code ):
		self.env_code = env_code

	# ############################################################
	# def set_lib_path(self): 
	# 	filedir = os.path.dirname( os.path.abspath(__file__) )		#get current directory
	# 	basedir = "/".join( filedir.split("/")[:-1] )				#get path above current directory
	# 	sys.path.append( basedir  )									#this would be the app dir
	# 	parentdir = "/".join( filedir.split("/")[:-3] )				#get path above current directory
		
	# 	sys.path.append(  parentdir )

	############################################################
	def get_env_config(self, xpath):  #area/category/sub_cat/name, or area/category//name, or area///name
		token = xpath.split('/')  
		if not 'ENV' in self.CFG: self.CFG['ENV'] = {}
		config = self.CFG['ENV'][self.env_code]
		for token_item in token:
			if not token_item in config: raise Exception( f"Path {xpath} [{token_item}] not found in current ENV[{self.env_code}]")  
			config = config[ token_item ]
		return config

	############################################################
	def get_app_config(self, xpath):
		token = xpath.split('/')  
		config = self.CFG['APP'] 
		for token_item in token:
			config = config[ token_item ]
		return config
		# breakpoint()

	############################################################
	def get_cfg(self, name, area, cat="_"    ):
			return self.CFG[ area ][cat][name]

	############################################################
	def get_env(self, name, area, cat="_"    ):
			return self.ENV.CFG[ area ][cat][name]

	############################################################
	def get_app(self, name, area, cat="_"    ):
			return self.APP.CFG[ area ][cat][name]

	##############################################################################################################
	# Load configuration 
	def load_app_config(self,  config_file ): 	
		raw_config = jsoncfg.load_config( config_file) 

		self.CFG[ 'APP' ] = {} 
		for raw_config_entry in raw_config[ 'app_config_list' ]:
			 self._load_config_entry(raw_config_entry, self.CFG[ 'APP' ])
		
		return self

	##############################################################################################################
	# Load configuration 
	def load_env_config(self, config_file ): 
		raw_config = jsoncfg.load_config( config_file) 
		
		for raw_env_config in raw_config[ 'env_config_list' ]:
			self.CFG[ 'ENV' ] = {}
			self.CFG[ 'ENV' ][ raw_env_config.env_code() ]  = {}
			cfg_path = self.CFG[ 'ENV' ][ raw_env_config.env_code() ]

			for raw_cfg_grp in raw_env_config['CFG']:	#Go through each file config entry
				self._load_config_entry(raw_cfg_grp, cfg_path)
		return self

	##############################################################################################################
	# Load configuration 
	def _load_config_entry(self, raw_cfg_grp , cfg_path):
		#Defaul t the config AREA, CATEGORY, SUB-CATEGORY if provided and create empty dict if equired
		if not raw_cfg_grp.area() in cfg_path: cfg_path[  raw_cfg_grp.area() ] = {}
		if not raw_cfg_grp.category() in cfg_path[  raw_cfg_grp.area() ]:  cfg_path[  raw_cfg_grp.area() ][ raw_cfg_grp.category() ] = {}
		if not raw_cfg_grp.sub_cat() in cfg_path[  raw_cfg_grp.area() ][ raw_cfg_grp.category() ]: cfg_path[  raw_cfg_grp.area() ][ raw_cfg_grp.category() ][ raw_cfg_grp.sub_cat() ] = {}

		#Get reference to the root item
		cfg_item = cfg_path[  raw_cfg_grp.area() ][ raw_cfg_grp.category() ][ raw_cfg_grp.sub_cat() ]
		
		#For each config item, then process - ether call func, convert jason, get value
		for raw_cfg_item in raw_cfg_grp[ 'config_list']:
			if 'func' in raw_cfg_item:	
				func_name =  raw_cfg_item.func()
				result = getattr(ConfigLoaderFunc,  func_name )(self, raw_cfg_item.param( {} ) )
				cfg_item[ raw_cfg_item.name() ] = result
			elif 'value_json' in raw_cfg_item: 
				cfg_item[ raw_cfg_item.name() ] = ast.literal_eval( raw_cfg_item.value_json(None) )
			else:
				cfg_item[ raw_cfg_item.name() ] = raw_cfg_item.value(None) 


	################################################################################################
	# Convert key config fields to dictionary to support flask input
	def _convert_to_flask(self, flask_list, obj_list):		#get key fields to flask
		flask_config = {}
		for item in flask_list:
			config_tokens = item.split('/')
			# breakpoint()
			for obj in obj_list:
				flask_config = {**flask_config, **self._to_flask_get_token( obj, 0, config_tokens) }
		
		flask_config['obj'] = self

		return flask_config

	##########################################################################################
	# Flatten the dictionary
	def _to_flask_get_token(self, obj, index, config_tokens):
		ret_hash = {}

		curr_token = config_tokens[index]	#Get the current token to process

		if index < ( len(config_tokens)-1): 	#If we still have more tokens
			if curr_token == "*":			#If current token is an '*', then loop through and merge with other items
				for key in obj:		
					ret_hash = {**ret_hash , **self._to_flask_get_token( obj[key], index+1, config_tokens) }
				return ret_hash
			else:
				next_node = obj.get( curr_token, None)
				if next_node: return {**ret_hash , **self._to_flask_get_token( next_node, index+1, config_tokens)}
				return ret_hash
		else:	#If this is last token, then copy over current records
			if curr_token == "*":
				for key in obj:
					ret_hash[ key] = obj[key] 
				return ret_hash
			else:
				return obj[ curr_token ]
				 