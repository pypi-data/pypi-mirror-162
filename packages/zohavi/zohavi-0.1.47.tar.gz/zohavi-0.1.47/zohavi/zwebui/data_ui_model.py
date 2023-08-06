import  json 
from jsonschema import validate as json_schema_validate
from jsonschema.exceptions import ValidationError


from zohavi.zwebui.web_field import WebField
from zohavi.zbase.staple import ZStaple
# from _def.common.selector import Selector
from dataobjtools.selector import Selector
import importlib

class DataUIModel(ZStaple):
	#####################################################################################
	def __init__(self,   form_field_validation_schema, session, logger ):

		super().__init__(app = None, logger = logger )

		DataUIModel.validate_schema( form_field_validation_schema )

		# self.update_obj_list = update_obj
		self.data_schema = form_field_validation_schema 
		
		self.web_schema = WebField( form_field_validation_schema, logger=logger )
		# self.logger = logger
		self.session = session

		# pass
	@staticmethod
	def validate_schema( json_input_schema):
		validation_schema = {
							"type": "array",
							"items": 
							{ 	"type" : "object",
								"properties" : 
								{ "module_name":{"type":"string" },
									"table_obj":{"type":"string" },
									"fields": 
									{ "type": "object",
										"patternProperties": 
										{	".*": 
											{ 	"type": "object",
												"properties": 
												{ 	"field_db":{"type":"string" },
													"key":{"type":"boolean" },
													"validation":{
																	"type": "object",
																	"properties": {
																					"required":{"type":"boolean"},
																					"text_min_len":{"type":"integer"},
																					"text_max_len":{"type":"integer"}
								} 	}	}	}	}	}	}	}
							}
		try:
			json_schema_validate( instance= json_input_schema , schema=validation_schema   )
		except  Exception as e:
			print(e)
			return False

		return True
 
	#####################################################################################
	def get_webfield_value( self, web_data, field_html_name):
		for field in web_data:	
			if field[ 'id'] == field_html_name: return field['value']
		
		return None

	#####################################################################################
	def get_field_schema( self, obj_name, field_html_name):
		
		for table_obj_rec in self.data_schema:
			if obj_name == table_obj_rec['table_obj']:
				return table_obj_rec['fields'].get(field_html_name)


		# table_obj_rec = self.data_schema.get( obj_name )

		# if table_obj_rec:
			
		return None

	#####################################################################################
	def _data_validate( self, submit_data ): 
		validation_result = {}
		self.log_debug("validating data")
		self.log_debug( submit_data )

		validation_result = self.web_schema.validate(  submit_data )
		if validation_result['success']: self.log_debug( 'Validation checks completed - result: passed' )
		else: self.log_error('Validation checks completed - result: failed')
		self.log_debug("****:" + json.dumps(   validation_result ) )
		
		return validation_result

	#####################################################################################
	def data_delete_ajax( self, submit_data ): 
		validation_result = self._data_validate( submit_data)
		if validation_result['success']:
			data_obj_list = self.data_delete( submit_data ) 
			return json.dumps({'success':True, 'data':  data_obj_list , 'result': validation_result, 'schema':self.data_schema }), 200
		else:
			return json.dumps({'success':False , 'result': validation_result }), 500 

	#####################################################################################
	def data_get_ajax( self, search_dict ):  
		
		data_obj_list = self.data_get( search_dict )
		
		if data_obj_list: return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema }), 200 

		return json.dumps({'success':False}), 500  

	#####################################################################################
	def data_get( self, search_dict, ret_db_obj=False):
		data_obj_list = []
		## Example of talbe fields in self.data_schema
		# 	"SiteMain":{ 	
		# 		# "table":"SiteMain",
		# 		# "fields":{
		# 					"si_site_id":{"field_db":"site_id",   "key":True},
		# 					"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
		# 					"si_site_code":{"field_db":"site_code",   "validation":{"required":True,  "text_max_len":5} },
		# 		# } }
		#Loop through each of the json table schame descriptions
		for obj_name, data_table in self.data_schema.items():
			# if obj_name in self.update_obj_list:
			db_fields = self.data_get_table_fields( data_table['fields'] , search_dict )
			self.log_debug(f"{obj_name} Read table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )	
			
			if db_fields:
				data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj'] )	#Get ref to table object name dynamically
				data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).all()

				for data_item in data_obj:
					if ret_db_obj: data_obj_list.append( data_item  )
					else: data_obj_list.append( data_item.to_dict()  )

		[ self.log_debug( f'Data from query: {data_item}')  for data_item in data_obj_list ] 
		return data_obj_list

	#####################################################################################
	def data_update_ajax( self, submit_data ): 
		if not submit_data:
			self.log_error('No data given')  
			return json.dumps({'success':False}), 500 
		else:
			validation_result = self._data_validate( submit_data)
			if validation_result['success']:
				data_obj_list = self.data_update( submit_data )
				# breakpoint()
				# webfield_mapping = self.data_get_web_fields( self.data_schema, data_obj_list)
				return json.dumps({'success':True, 'data':  data_obj_list , 'result': validation_result, 'schema':self.data_schema  }), 200
				# return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema  }), 200
			else:
				self.log_error('Could not update data as valdation failed')  
				return json.dumps({'success':False,  'result': validation_result } ), 500 



	#####################################################################################
	def data_delete(self, web_data):
		for data_table in self.data_schema:
			db_fields = self.data_get_table_fields( data_table['fields'] , web_data )
			self.log_debug(f" Delete table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )

			data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj']  )	#Get ref to table object name dynamically
			data_obj = None
			if db_fields['keys']: 
				data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).delete()
				self.session.commit()
		return True
			# breakpoint()
	#####################################################################################
	def data_update(self, web_data):
		data_obj_list = []
		# breakpoint()
		## Example of talbe fields in self.data_schema
		# 	"SiteMain":{ 	
		# 		# "table":"SiteMain",
		# 		# "fields":{
		# 					"si_site_id":{"field_db":"site_id",   "key":True},
		# 					"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
		# 					"si_site_code":{"field_db":"site_code",   "validation":{"required":True,  "text_max_len":5} },
		# 		# } }
		#Loop through each of the json table schame descriptions
		for data_table in self.data_schema :
			# if obj_name in self.update_obj_list:
			db_fields = self.data_get_table_fields( data_table['fields'] , web_data )
			self.log_debug(f"Modify table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )	
			
			data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj'] )	#Get ref to table object name dynamically
			data_obj = None

			#Search to see if the record exists
			if db_fields['keys']: 
				# breakpoint()
				data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).first()
			
			if data_obj:  #If found, then update fields
				for db_field_name in db_fields['fields']:
					setattr( data_obj, db_field_name, db_fields['fields'][ db_field_name ]  )
			else:	#If not found, create new object
				data_obj = data_class_ref( **db_fields['fields'] )
				self.session.add(data_obj)  
				self.session.flush()	#specifically flush to get the ID number
			data_obj_list.append( data_obj.to_dict()  )
			# else: 
			# 	self.log_debug(f"Skipping [{obj_name}] as it is not in the schema list provided[{self.update_obj_list}]")
		
		self.session.commit()
		
		return data_obj_list 


	#####################################################################################
	def data_get_table_fields(self, table_schema_fields, web_data ):
		data_obj_list = []
		db_fields = {'keys':{}, 'fields':{} } 
		# breakpoint()
		for field_name, field in table_schema_fields.items():	#Loop through each of the fields in a given table
			
			new_field = Selector().dict_search( web_data, {'id': field_name  } )
			if not new_field: 
				self.log_error(f'Could not find key [{field_name}] within web_data:[{web_data}]')
			else:
				# self.logger.debug(f"Adding field [{field_name}] value of: [{ new_field['value']  }]")
				if field.get("key") :
					if new_field['value']: db_fields[ "keys"][ field["field_db"] ] = new_field['value'] 
				else:
					db_fields[ "fields"][ field["field_db"] ] = new_field['value'] 

		self.log_debug(f"fields: {db_fields}")
		return db_fields 

 

# class DataUIModel(ZStaple):
# 	#####################################################################################
# 	def __init__(self, update_obj, form_field_validation_schema, session, logger ):

# 		super().__init__(app = None, logger = logger )

# 		self.update_obj_list = update_obj
# 		self.data_schema = form_field_validation_schema 
# 		self.web_schema = WebField( form_field_validation_schema, logger=logger )
# 		# self.logger = logger
# 		self.session = session

# 		# pass

# 	#####################################################################################
# 	def get_webfield_value( self, web_data, field_html_name):
# 		for field in web_data:	
# 			if field[ 'id'] == field_html_name: return field['value']
		
# 		return None

# 	#####################################################################################
# 	def get_field_schema( self, obj_name, field_html_name):
# 		table_obj_rec = self.data_schema.get( obj_name )

# 		if table_obj_rec:
# 			return table_obj_rec['fields'].get(field_html_name)
# 		return None

# 	#####################################################################################
# 	def _data_validate( self, submit_data ): 
# 		self.log_debug("validating data")
# 		self.log_debug( submit_data )

# 		if self.web_schema.validate(  submit_data ):
# 			self.log_debug('validation ok')
# 			return True
# 		return False

# 	#####################################################################################
# 	def data_delete_ajax( self, submit_data ): 
# 		if self._data_validate( submit_data):
# 			data_obj_list = self.data_delete( submit_data ) 
# 			return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema }), 200
# 		else:
# 			self.log_error('valdation failed')  
# 			return json.dumps({'success':False}), 500 

# 	#####################################################################################
# 	def data_get_ajax( self, search_dict ):  
		
# 		data_obj_list = self.data_get( search_dict )
		
# 		if data_obj_list: return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema }), 200 

# 		return json.dumps({'success':False}), 500  

# 	#####################################################################################
# 	def data_get( self, search_dict, ret_db_obj=False):
# 		data_obj_list = []
# 		## Example of talbe fields in self.data_schema
# 		# 	"SiteMain":{ 	
# 		# 		# "table":"SiteMain",
# 		# 		# "fields":{
# 		# 					"si_site_id":{"field_db":"site_id",   "key":True},
# 		# 					"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
# 		# 					"si_site_code":{"field_db":"site_code",   "validation":{"required":True,  "text_max_len":5} },
# 		# 		# } }
# 		#Loop through each of the json table schame descriptions
# 		for obj_name, data_table in self.data_schema.items():
# 			if obj_name in self.update_obj_list:
# 				db_fields = self.data_get_table_fields( data_table['fields'] , search_dict )
# 				self.log_debug(f"{obj_name} Read table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )	
				
# 				if db_fields:
# 					data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj'] )	#Get ref to table object name dynamically
# 					data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).all()

# 					for data_item in data_obj:
# 						if ret_db_obj: data_obj_list.append( data_item  )
# 						else: data_obj_list.append( data_item.to_dict()  )

# 		[ self.log_debug( f'Data from query: {data_item}')  for data_item in data_obj_list ] 
# 		return data_obj_list

# 	#####################################################################################
# 	def data_update_ajax( self, submit_data ): 
# 		if not submit_data:
# 			self.log_error('No data given')  
# 			return json.dumps({'success':False}), 500 
# 		elif self._data_validate( submit_data):
# 			data_obj_list = self.data_update( submit_data )
# 			# breakpoint()
# 			# webfield_mapping = self.data_get_web_fields( self.data_schema, data_obj_list)
# 			return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema  }), 200
# 			# return json.dumps({'success':True, 'data':  data_obj_list , 'schema':self.data_schema  }), 200
# 		else:
# 			self.log_error('valdation failed')  
# 			return json.dumps({'success':False}), 500 



# 	#####################################################################################
# 	def data_delete(self, web_data):
# 		for obj_name, data_table in self.data_schema.items():
# 			db_fields = self.data_get_table_fields( data_table['fields'] , web_data )
# 			self.log_debug(f"{obj_name} Delete table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )

# 			data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj']  )	#Get ref to table object name dynamically
# 			data_obj = None
# 			if db_fields['keys']: 
# 				data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).delete()
# 				self.session.commit()
# 		return True
# 			# breakpoint()
# 	#####################################################################################
# 	def data_update(self, web_data):
# 		data_obj_list = []
# 		# breakpoint()
# 		## Example of talbe fields in self.data_schema
# 		# 	"SiteMain":{ 	
# 		# 		# "table":"SiteMain",
# 		# 		# "fields":{
# 		# 					"si_site_id":{"field_db":"site_id",   "key":True},
# 		# 					"si_site_name":{"field_db":"site_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
# 		# 					"si_site_code":{"field_db":"site_code",   "validation":{"required":True,  "text_max_len":5} },
# 		# 		# } }
# 		#Loop through each of the json table schame descriptions
# 		for obj_name, data_table in self.data_schema.items():
# 			if obj_name in self.update_obj_list:
# 				db_fields = self.data_get_table_fields( data_table['fields'] , web_data )
# 				self.log_debug(f"{obj_name} Modify table: {data_table['module_name']}::{ data_table['table_obj'] } with search keys {db_fields['keys'] }" )	
				
# 				data_class_ref = getattr(importlib.import_module( data_table['module_name'] ), data_table['table_obj'] )	#Get ref to table object name dynamically
# 				data_obj = None

# 				#Search to see if the record exists
# 				if db_fields['keys']: data_obj = self.session.query( data_class_ref ).filter_by( **db_fields['keys'] ).first()
				
# 				if data_obj:  #If found, then update fields
# 					for db_field_name in db_fields['fields']:
# 						setattr( data_obj, db_field_name, db_fields['fields'][ db_field_name ]  )
# 				else:	#If not found, create new object
# 					data_obj = data_class_ref( **db_fields['fields'] )
# 					self.session.add(data_obj)  
# 					self.session.flush()	#specifically flush to get the ID number
# 				data_obj_list.append( data_obj.to_dict()  )
# 			else: 
# 				self.log_debug(f"Skipping [{obj_name}] as it is not in the schema list provided[{self.update_obj_list}]")
		
# 		self.session.commit()
		
# 		return data_obj_list 


# 	#####################################################################################
# 	def data_get_table_fields(self, table_schema_fields, web_data ):
# 		data_obj_list = []
# 		db_fields = {'keys':{}, 'fields':{} } 
# 		# breakpoint()
# 		for field_name, field in table_schema_fields.items():	#Loop through each of the fields in a given table
			
# 			new_field = Selector().dict_search( web_data, {'id': field_name  } )
# 			if not new_field: 
# 				self.log_error(f'Could not find key [{field_name}] within web_data:[{web_data}]')
# 			else:
# 				# self.logger.debug(f"Adding field [{field_name}] value of: [{ new_field['value']  }]")
# 				if field.get("key") :
# 					if new_field['value']: db_fields[ "keys"][ field["field_db"] ] = new_field['value'] 
# 				else:
# 					db_fields[ "fields"][ field["field_db"] ] = new_field['value'] 

# 		self.log_debug(f"fields: {db_fields}")
# 		return db_fields 


# 	# #####################################################################################
# 	# def data_get_web_fields(self, table_schema_fields, db_data ):
# 	# 	data_obj_list = []
# 	# 	web_fields = { } 

# 	# 	for schema in table_schema_fields:
# 	# 		for field_name in table_schema_fields[schema]['fields']:
# 	# 			field_rec = table_schema_fields[schema]['fields'][field_name]
# 	# 			if field_rec['field_db'] in db_data[0]:		#See if the database field name is in the data row.  
# 	# 														#No need to check all rows, just check the first row 
# 	# 														#since all rows schema is the same
# 	# 				web_fields[ field_rec['field_db'] ]  =  field_name
# 	# 	return web_fields 