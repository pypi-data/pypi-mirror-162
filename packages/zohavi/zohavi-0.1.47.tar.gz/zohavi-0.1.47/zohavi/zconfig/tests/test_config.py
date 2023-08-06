import unittest
unittest.TestLoader.sortTestMethodsUsing = None

import sys, os, jsoncfg
sys.path.insert(0, '../../../')


from mclogger import MCLogger
from zohavi.zconfig.config_manager import CoreConfig 
from zohavi.zconfig.models import MDL_Config
from jsondbupload import JsonDBUpload

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
 

sys_config1 = """{
					"dev":{
						"host":"0.0.0.0",
						"port":"4100" ,
						"log_file":"log_test_dev.txt",
						"db_core":"postgresql:///test1"
					},
					"qa":{
						"host":"0.0.0.0",
						"port":"4200" ,
						"log_file":"log_test_qa.txt",
						"db_core":"postgresql:///test1"
					},
					"prd":{
						"host":"0.0.0.0",
						"port":"4300" ,
						"log_file":"log_test_prd.txt",
						"db_core":"postgresql:///test1"
					},
			}"""

logger = MCLogger('log.txt')

########
sccfg = CoreConfig(config_str=sys_config1, base_dir=os.getcwd() )

# breakpoint()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = sccfg.get_env_config('dev').db_core
db = SQLAlchemy(app)
migrate = Migrate(app, db)
cdb = MDL_Config( logger=None, db=db)
db.drop_all()
db.create_all()

class TestProc(unittest.TestCase):
	def test_0000_setup_app_config(self):
		pass
	
	def test_0010_setup_database(self):	
		JsonDBUpload(db, logger).update_tables_from_file( 'test_db_config_defaults.json') 

	
	def test_0020_load_core_config_str(self):
		sccfg = CoreConfig( config_str=sys_config1, base_dir=os.getcwd() )

		raw_cfg = jsoncfg.loads_config( sys_config1 )
		# breakpoint()
		logger.debug( os.getcwd() )
		self.assertEqual( sccfg.get_env_config('dev').env , 'dev'  )
		self.assertEqual( sccfg.get_env_config('dev').host , raw_cfg.dev.host()  )
		self.assertEqual( sccfg.get_env_config('dev').port , raw_cfg.dev.port()  )
		self.assertEqual( sccfg.get_env_config('dev').log_file , raw_cfg.dev.log_file()  )
		self.assertEqual( sccfg.get_env_config('dev').db_core , raw_cfg.dev.db_core()  )
		self.assertEqual( sccfg.get_env_config('dev').log_full_path , raw_cfg.dev.log_file()   )
	

	def test_0030_load_core_config_file(self):
		sccfg = CoreConfig( filename='sys_config.json', base_dir=os.getcwd() )

		raw_cfg = jsoncfg.load_config( 'sys_config.json' )
		# breakpoint()
		logger.debug( os.getcwd() )
		self.assertEqual( sccfg.get_env_config('dev').env , 'dev'  )
		self.assertEqual( sccfg.get_env_config('dev').host , raw_cfg.dev.host()  )
		self.assertEqual( sccfg.get_env_config('dev').port , raw_cfg.dev.port()  )
		self.assertEqual( sccfg.get_env_config('dev').log_file , raw_cfg.dev.log_file()  )
		self.assertEqual( sccfg.get_env_config('dev').db_core , raw_cfg.dev.db_core()  )
		self.assertEqual( sccfg.get_env_config('dev').log_full_path , raw_cfg.dev.log_file()   )
	

	def test_0040_load_core_config_path_str(self):

		sys_config2 = """{	
					"dev":{
						"host":"0.0.0.0",
						"port":"4100" ,
						"log_file":"!/log_test_dev.txt",
						"db_core":"postgresql:///test1"
					} 
			}"""

		sccfg = CoreConfig(config_str=sys_config2, base_dir=os.getcwd() )
		raw_cfg = jsoncfg.loads_config( sys_config2 )
		self.assertEqual( sccfg.get_env_config('dev').log_full_path , raw_cfg.dev.log_file().replace('!',  os.getcwd())   )

	def test_0050_flask_config(self):
		config = cdb.to_flask_config()
		self.assertTrue( 'SECRET_KEY' in config.keys() )
		self.assertTrue( 'SQLALCHEMY_TRACK_MODIFICATIONS' in config.keys() )

	def test_0060_query_get_onfig_xpath(self):
		self.assertTrue( cdb.get_config(config_str='SYS/DIR//ENV_BASE_DIR' ) != None )
		
	def test_0061_query_get_onfig_xpath(self):
		self.assertTrue( cdb.get_config(config_str='SYS///ENV_BASE_DIRxx' ) == None )

	def test_0062_query_get_onfig_xpath(self):
		self.assertTrue( cdb.get_config(config_str='SYS/x/x/ENV_BASE_DIR' ) == None )

	def test_0070_query_set_onfig_xpath(self):
		cdb.set_config(config_str='SYS/DIR//ENV_BASE_DIR', value='123' )
		self.assertTrue( cdb.get_config(config_str='SYS/DIR//ENV_BASE_DIR' ).value == '123' )

	def test_0071_query_set_onfig_xpath_new_item(self):
		cdb.set_config(config_str='SYS/DIR//LOG_FILE', value='log.txt' )
		self.assertTrue( cdb.get_config(config_str='SYS/DIR//LOG_FILE' ).value == 'log.txt' )
	
	def test_0072_query_set_onfig_xpath_new_config_and_item(self):
		cdb.set_config(config_str='MAIN///LOG_FILE', value='log.txt' )
		self.assertTrue( cdb.get_config(config_str='MAIN///LOG_FILE' ).value == 'log.txt' )