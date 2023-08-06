import json, datetime 

from sqlalchemy import DateTime, Column

from zohavi.zdb.models import TBL_Default
from zohavi.zbase.staple import ZStaple
from prepost import PreCond


############################################################################################################
############################################################################################################
class MDL_Config(ZStaple):
	def __init__(self, logger, db):
		super().__init__(logger=logger, app=None)
		self.db = db

		class TBL_Config(db.Model, TBL_Default):
			__tablename__ = 'config' 
			id = db.Column(db.Integer(), primary_key=True)
			area 		= db.Column(db.String(25) ) 
			category 	= db.Column(db.String(25) ) 
			sub_cat		= db.Column(db.String(25) ) 
			_config_items = db.relationship('TBL_ConfigItem', cascade='all,delete',  passive_deletes=True, back_populates="_config")
		
		class TBL_ConfigItem(db.Model, TBL_Default):
			__tablename__ = 'config_item' 
			id = db.Column(db.Integer(), primary_key=True)
			config_id = db.Column(db.Integer(), db.ForeignKey( 'config.id' , ondelete='CASCADE') ) 
			env =  db.Column(db.String(10) ) 
			name = db.Column(db.String(100) ) 
			value = db.Column(db.String(255) ) 		
			flask_name = db.Column(db.String(100) ) 
			_config = db.relationship('TBL_Config',   back_populates="_config_items")
	
		self._tables = {}
		self._tables['TBL_Config'] 	   = TBL_Config
		self._tables['TBL_ConfigItem'] = TBL_ConfigItem
	
	################################################################################################################
	def get_tables(self):
		return self._tables

	################################################################################################################
	@PreCond.matches_pattern( config_str='.*\/.*\/.*\/.*')
	def get_config(self, config_str):
		xpath = config_str.split('/')
		cls_tbl_item = self._tables['TBL_ConfigItem']
		cls_tbl_main = self._tables['TBL_Config']

		item_list = self.db.session.query( cls_tbl_item ).filter( cls_tbl_item.name == xpath[3] ).all()
		for item in item_list:
			if item._config.area == xpath[0] and item._config.category == xpath[1] and item._config.sub_cat == xpath[2]:
				return item
		return None

	################################################################################################################
	@PreCond.matches_pattern( config_str='.*\/.*\/.*\/.*')
	def set_config(self, config_str, value, flask_name = None):
		
		item = self.get_config( config_str = config_str )
		# 
		if item: item.value = value
		else:
			#check if the main entry exists
			xpath = config_str.split('/')
			tbl_main = self._set_config_main( xpath[0], xpath[1], xpath[2] )
			tbl_item = self._tables['TBL_ConfigItem']()
			tbl_item.name = tbl_item.flask_name = xpath[3]
			if flask_name: tbl_item.flask_name = flask_name
			tbl_item.value = value
			tbl_item._config = tbl_main
			self.db.session.add( tbl_item )
		self.db.session.commit()		 
	
	def _set_config_main(self, area, category, sub_cat):
		cls_tbl_main = self._tables['TBL_Config']
		config_main = self.db.session.query( cls_tbl_main ).filter( cls_tbl_main.area == area, cls_tbl_main.category == category, cls_tbl_main.sub_cat == sub_cat).first()
		if not config_main:
			config_main = cls_tbl_main()
			config_main.area = area
			config_main.category = category
			config_main.sub_cat = sub_cat
			self.db.session.add(config_main)
		return config_main
			


	def to_flask_config(self):
		config = {}

		cls_config_item = self._tables['TBL_ConfigItem']
		data_flask_config = self.db.session.query( cls_config_item ).filter( cls_config_item.flask_name != '' ).all()
		# breakpoint()
		for data_item in data_flask_config:
			config[ data_item.flask_name ]= data_item.value
		return config


	