import unittest
unittest.TestLoader.sortTestMethodsUsing = None

import sys, os, jsoncfg
sys.path.insert(0, '../../../')


# from mclogger import MCLogger
from zohavi.zerrors.routes import ErrorsView 
from zohavi.zcore.appcore import AppCore 
# from zohavi.zconfig.models import MDL_Config
# from jsondbupload import JsonDBUpload

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from zohavi.zconfig.config_manager import CoreConfig

sys_config = """{
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

sccfg = CoreConfig( config_str= sys_config  )


class TestCore(unittest.TestCase):

    def test_0010_start_app(self):
        app = Flask(__name__)
        myapp = AppCore(app, sccfg, 'dev' )

        myapp.setup_blueprint_dyn( 	bp_module_class_str ='zohavi.zerrors#bp', 
                                    route_module_class_str='zohavi.zerrors.routes#ErrorsView',
                                    url_prefix='/' )
        app.run(host="0.0.0.0", port=8601)