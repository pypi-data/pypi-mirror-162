import unittest
unittest.TestLoader.sortTestMethodsUsing = None

import sys, os, jsoncfg
sys.path.insert(0, '../../../')
sys.path.insert(0, '../../../../')
sys.path.insert(0, '../../../../../')

from flask import Flask
from mclogger import MCLogger
from mclogger.mclogger import MCLogger

from zohavi.zcore.appcore import AppCore 
from zohavi.zdb.models import TBL_Default
from zohavi.zwebui.data_ui_model import DataUIModel


logger = MCLogger( 'test_log.txt' )

site_update_schema = {
							"SiteMain":[{ 	
								"module_name":"test_zwebui",
								"table_obj": "SiteMain",
								"fields":{
											"si_site_id":{"field_db":"id",   "key":True},
											"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
											"si_site_code":{"field_db":"site_code", "validation":{"required":True,  "text_max_len":5} },
											"si_site_desc":{"field_db":"site_desc", "validation":{"required":False,  "text_max_len":200} }
								}
							}]
					}

from sqlalchemy import Column, Integer, String 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

############################################################################################################
############################################################################################################
class SiteMain( Base ,  TBL_Default):
	__tablename__ = 'site_main' 
	id = Column(Integer(), primary_key=True)
	site_name = Column(String(100) ) 
	site_desc = Column(String(200) ) 
	site_code = Column(String(5) )  
	cfg_main_runme 	= Column(String(10) ) #dev, qa, prod  
# 	_env_list = relationship("SiteEnv", backref=backref("site_env" ), lazy='select') 
	
# ############################################################################################################
# ############################################################################################################
# class SiteEnv(Model,  TBL_Default): 
# 	ENV_STATUS_NEW = 'NEW'
# 	ENV_STATUS_GEN = 'GENERATING'
# 	ENV_STATUS_ACT = 'ACTIVE'
# 	ENV_STATUS_DIS = 'DISABLED'
# 	ENV_STATUS_DEL = 'DELETED'

# 	__tablename__ 	= 'site_env' 
# 	id 				= Column(Integer(), primary_key=True)
# 	site_id 		= Column(Integer(), ForeignKey( 'site_main.id'  ) )
# 	_site 			= relationship("SiteMain", backref=backref("site_main" ), lazy='joined')
# 	env_code 		= Column(String(5) ) #dev, qa, prod
# 	env_is_root		= Column(Boolean(), default=False )  
# 	env_desc		= Column(String(20) ) #dev, qa, prod
# 	env_setup_status = Column(String(10), default=ENV_STATUS_NEW ) #NEW, GENERATING, ACTIVE, DISABLED, DELETED

# 	prev_env_id		= Column(Integer(), ForeignKey( 'site_env.id'  ) )

class TestCore(unittest.TestCase):
	def setUp(self):

		engine = create_engine('sqlite:///:memory:')
		Session = sessionmaker(bind=engine)
		self.session = Session()

		Base.metadata.create_all(engine)
		self.session.add( SiteMain(site_name='twitterbot', site_desc='Twitter Bot', site_code='tb', cfg_main_runme='dev'))
		self.session.commit()

	########################################################################
	# Test creating a class
	def test_0001_validate_schema(self):
		logger.debug('.')
		validate_schema = {
							"SiteMain":[{ 	
								"module_name":"test_zwebui",
								"table_obj": "SiteMain",
								"fields":{
											"si_site_id":{"field_db":"id",   "key":True},
											"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":5} },
											"si_site_code":{"field_db":"site_code", "validation":{"required":True,  "text_max_len":5} },
											"si_site_desc":{"field_db":"site_desc", "validation":{"required":False,  "text_max_len":200} }
								}
							}]
					}

		self.assertTrue(  DataUIModel.validate_schema( validate_schema["SiteMain"] )  )
		



	#######################################################################
	#Test creating a class
	def test_0010_create_instance(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 
		self.assertTrue( data_ui )
 		
	########################################################################
	# Test getting field info
	def test_0020_get_field_schema(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 

		site_name = data_ui.get_field_schema('SiteMain', "si_site_name")
		print( site_name )
		self.assertTrue( site_name )

	########################################################################
	# Test updating fieleds - create records with validated fields
	def test_0025_create_record(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 
		json_update = 	[
							{ "id":"si_site_id", "value":""},
							{ "id":"si_site_name", "value":"abc1"},
							{ "id":"si_site_desc", "value":"abc2"},
							{ "id":"si_site_code", "value":"abc3"}
						]
		ret_data = data_ui.data_update_ajax( json_update )

		item = self.session.query( SiteMain).filter_by( site_name='abc1' ).first()
		self.assertEquals( ret_data[1], 200  )
		
		
		self.assertTrue( item  )

	########################################################################
	# Test updating fieleds - create records with failed validated fields
	def test_0025_create_record(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 
		json_update = 	[
							{ "id":"si_site_id", "value":""},
							{ "id":"si_site_name", "value":"ccccccccccccccccccccccccccccccccccccc"},
							{ "id":"si_site_desc", "value":"abc2"},
							{ "id":"si_site_code", "value":"abc3"}
						]
		ret_data = data_ui.data_update_ajax( json_update )
		# breakpoint()
		logger.debug( ret_data )

		item = self.session.query( SiteMain).filter_by( site_name='abc1' ).first()
		self.assertEquals( ret_data[1], 500  )
		self.assertFalse( item  )

	########################################################################
	# Test updating fieleds
	def test_0030_update_record(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 
		json_update = 	[
							{ "id":"si_site_id", "value":""},
							{ "id":"si_site_name", "value":"abc1"},
							{ "id":"si_site_desc", "value":"abc2"},
							{ "id":"si_site_code", "value":"abc3"}
						]
		ret_data = data_ui.data_update_ajax( json_update )
		logger.debug( ret_data )
		item = self.session.query( SiteMain).filter_by( site_name='abc1' ).first()
		self.assertEquals( ret_data[1], 200  )
		self.assertTrue( item  )

	########################################################################
	# Test updating fieleds but iwht missing fields
	def test_0040_update_record_with_missing_fields(self):
		logger.debug('.')
		data_ui = DataUIModel( site_update_schema['SiteMain']  , self.session, logger ) 
		json_update = 	[
							#{ "id":"si_site_id", "value":""}, <--- omit to test failures
							# { "id":"si_site_name", "value":"abc1"},
							# { "id":"si_site_desc", "value":"abc2"},
							# { "id":"si_site_code", "value":"abc3"}
						]
		ret_data = data_ui.data_update_ajax( json_update )
		item = self.session.query( SiteMain).filter_by( site_name='abc1' ).first()
		 
		self.assertEquals( ret_data[1], 500  )
		self.assertFalse( item  )

	########################################################################
	# Test updating fieleds but iwht missing fields
	

#  #################################################################
#  #################################################################


if __name__ == '__main__':
    unittest.main()