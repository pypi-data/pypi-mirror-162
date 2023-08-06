import unittest

import os , sys
# import sys, os, jsoncfg
sys.path.insert(0, '../../../')


from flask import Flask #, current_app
from mclogger import    MCLogger 
from pathlib import Path
from zohavi.zconfig.config_manager import CoreConfig

# base_dir = Path( os.getcwd() )
sccfg = CoreConfig( f'sys_config.json' )

from zohavi.zcore.appcore import AppCore

class TestCore(unittest.TestCase):

    def test_0010_start_app(self):
        app = Flask(__name__)
        myapp = AppCore(app, sccfg, 'dev' )

        port = myapp.get_config('SYS///PORT')
        # breakpoint()
        self.assertTrue( port.value == '4100')
		# self.assertTrue( myapp.get_config( config_str='SYS///LOG_FILE', value=sccfg.get_env_config( env ).log_file )
		# self._ref_config.set_config( config_str='SYS///HOST', value=sccfg.get_env_config( env ).host )
		# self._ref_config.set_config( config_str='SYS///PORT', value=sccfg.get_env_config( env ).port )
		# self._ref_config.set_config( config_str='SYS/DIR//BASE_DIR', value=sccfg.get_env_config( env ).base_dr )
		# self._ref_config.set_config( config_str='SYS/DB//CORE', value=sccfg.get_env_config( env ).db_core )