import re, json 
from dataclasses import dataclass, asdict as dataclasses_asdict 
from dataclasses_json import dataclass_json

from typing import Callable

from zohavi.zbase.staple import ZStaple
from mclogger import MCLogger

class WebField( ZStaple ):
	def __init__(self, tables, app=None, logger=None):
		super().__init__(app = app, logger = logger )
		self.debug = True

		self._tables = tables
		self._table_lookup = self._calc_web_table_lookup()

		self.log_debug(f"Stored: {json.dumps(tables) }")

	def get_field(self, field_name):
		# for field in self._fields:
		# 	if field['id'] == field_name: return field
		return self._fields[field_name]
 
	def _calc_web_table_lookup(self):
		table_lookup = {}
		for index, table_rec in enumerate( self._tables ):
		#create new dict entry for each of the web fields
			for web_field_name in table_rec['fields'].keys():
				table_lookup[ web_field_name ] =  table_rec 
		return table_lookup

	#############################################################################################################
	#Validate form data in json format
	@MCLogger.logfunc_cls('logger')
	def validate(self, data):
		# validation_ok = True 
		result = { 'success': True, 'validations':[] }	#Assume successful

		self.log_debug( "validating:" + json.dumps(data ) )
		self.log_debug( "Master:" + json.dumps(self._tables ) )

		for data_row in data:	#loop through each web data field
			if not 'id' in data_row: raise Exception( f"Missing field [id] in {data_row}.  Json format shoudl have 'id' and 'value' elements")

			web_field_name = data_row['id']
			# breakpoint()
			if not web_field_name in self._table_lookup: raise Exception( f"[{web_field_name}] from submit data not found in schema { self._tables }")
			# table_ref = self._field_lookup[ web_field_name ]
			
			#Use the reverse lookup to find the table associated with the field
			field_info = self._table_lookup[ web_field_name ]['fields'][ web_field_name ]

			if field_info.get('validation', False):  #has validation
				self.log_debug( f" Checking validation {web_field_name}=>[{data_row['value']}] Rule:{json.dumps( field_info['validation']) } ") 
				# breakpoint()
				result = self._validate_run_validation_rule(web_field_name, data_row['value'] , field_info['validation'], result  )

			if field_info.get('transform', False):  #has transformation
				data_row['value'] = self._run_transformation( data_row['value'] , field_info['transform'] )
		
		return result


	#############################################################################################################
	#
	def _run_transformation(self, data_value, transform_rules):
		self.log_debug( f" data_value={data_value}; transform={json.dumps(transform_rules) }")

		ret_value = data_value
		for rule in transform_rules: 
			func = getattr(Transform, rule, Transform._func_not_found)  
			ret_value = func( ret_value , transform_rules[rule] )

		return ret_value


	#############################################################################################################
	#Run the actual validation rule
	def _validate_run_validation_rule(self, web_field_name, data_value, validation_rules, validation_results:dict ):
		result = validation_results
		if not result: result = { 'success': True, 'validations':[] }
		# validation_ok = True 
		# if not data_value: breakpoint()
		# breakpoint()
		self.log_debug( f" data_value={data_value}; validation_rule={json.dumps(validation_rules)}")
		if not data_value and 'required' in validation_rules.keys() and validation_rules['required'] == False: return result
		for rule in validation_rules: 
			func = getattr(Validate, rule, Validate._func_not_found)  
			ret_result = func( data_value , validation_rules[rule], self.log_error )	#Pass reference to error message for failed validatinos
			ret_result.web_field_name = web_field_name
			result['validations'].append(  dataclasses_asdict(ret_result ) )
			log_message = f"Validation check [{rule}:{validation_rules[rule]}] on [{data_value}] => {ret_result}"
			# if ret_check:
			# 	self.log_debug( log_message ) 
			# else:
			# 	validate_fail_reason['01'] = log_message
			# 	self.log_error( log_message )

			result['success'] = result['success'] and ret_result.success

		self.log_debug("Returning validation check from :" + json.dumps(validation_rules) + " => " + str(result['success']) )
		return result
 


class Transform(ZStaple):

	@staticmethod
	def _func_not_found( value, param) :
		Transform.log_error("transformation function not found")

	#############################################################################################################
	#Check if the current 
	@staticmethod
	def to_bool(value, param) :
		return Transform._map_value( value, {'':False, 'false':False, '0':False, 
											'True':True, 'true':True, '1':True, True:True} )
	@staticmethod
	def _map_value(value, map):
		return map.get( value, None)

@dataclass_json
@dataclass
class ValidateResult():
	web_field_name: str = "" 
	success: bool = False
	rule: str = ""
	value: object = None
	param: object = None
	err_no: str = ""
	err_msg: str = ""
	
	

class Validate(ZStaple):
	#############################################################################################################
	#Check if the current 
	@staticmethod
	def _get_data_field_field(  value, field_name):
		for data_fld in value:	#find the relevant data field in there
			if data_fld['id'] == field_name:
				return data_fld
		return None

	#############################################################################################################
	#validation function not found
	@staticmethod
	def _func_not_found( value, param, log_err_func: Callable =print ):
		vr = ValidateResult( rule='??', value=value,  param=param , err_no="VAL_010", err_msg='Validation Rule passed not found')
		Validate.log( vr.err_msg , log_err_func)
		return vr

	#############################################################################################################
	#Check that field is required 
	@staticmethod
	def required(  value, param, log_err_func: Callable =print ):  
		vr = ValidateResult( rule='required', value=value,  param=param )
		if not param: vr.success = True
		elif value: vr.success = True  
		else:  #e.g. parameter is present, and value not given
			vr.success = False  
			vr.err_no = "VAL_020"
			vr.err_msg = 'Required value not given'
			Validate.log( vr.err_msg , log_err_func)

		return vr 

	#############################################################################################################
	#Check that field has min length as required
	@staticmethod
	def text_min_len(  value, param, log_err_func: Callable =print  ): 
		vr = ValidateResult( rule='text_min_len', value=value,  param=param )

		if len( str( value  ) ) >= param: vr.success = True
		else: 
			vr.success = False 
			vr.err_no = "VAL_030"
			vr.err_msg = f"Value [{value}] should be minimum length of {param}, but actual length is {len( str( value  ) )}"
			Validate.log( vr.err_msg , log_err_func)
		return vr 

	#############################################################################################################
	#Check that field has max length as required
	@staticmethod
	def text_max_len(  value, param,log_err_func: Callable =print  ): 
		vr = ValidateResult( rule='text_max_len', value=value,  param=param )

		if len( str( value ) ) <= param: vr.success= True
		else: 
			vr.success = False 
			vr.err_no = "VAL_040"
			vr.err_msg = f"Value [{value}] should be max length of {param}, but actual length is {len( str( value  ) )}"
			Validate.log( vr.err_msg , log_err_func)
		
		return vr 

	#############################################################################################################
	#Check that number is gte
	@staticmethod
	def num_gte(   value, param, log_err_func: Callable =print ): 
		vr = ValidateResult( rule='num_gte', value=value,  param=param )
		if int( value ) >= int(param): vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_050"
			vr.err_msg = f"Value [{value}] should be greater than or equal to {param}, but actual is { int( value )}"
			Validate.log( vr.err_msg , log_err_func)
		
		return vr 

	#############################################################################################################
	#Check that number is gte
	def num_lte(  value, param , log_err_func: Callable =print  ): 
		vr = ValidateResult( rule='num_lte', value=value,  param=param )
		if int( value ) <= int(param): vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_060"
			vr.err_msg = f"Value [{value}] should be less than or equal to {param}, but actual is { int( value )}"
			Validate.log( vr.err_msg , log_err_func)
		return vr 

	#############################################################################################################
	#Check that field has max length as required
	@staticmethod
	def is_url(  value, param=None, log_err_func: Callable =print ):  
		vr = ValidateResult( rule='is_url', value=value,  param=param )
		url_re = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
		url = re.findall(url_re, value )
		if url:  vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_070"
			vr.err_msg = f"[{value}] is not an URL"
			Validate.log( vr.err_msg , log_err_func)
		return vr 

	#############################################################################################################
	#Check that field has max length as required
	@staticmethod
	def is_ip(  value, param=None, log_err_func: Callable =print   ):  
		vr = ValidateResult( rule='is_ip', value=value,  param=param )
		url_re = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
		url = re.findall(url_re, value )
		
		if url:  vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_080"
			vr.err_msg = f"[{value}] is not an IP"
			Validate.log( vr.err_msg , log_err_func)
		return vr 


	#############################################################################################################
	#Check that number is gte
	@staticmethod
	def is_unix_path(  value , param=None, log_err_func: Callable =print  ): 
		vr = ValidateResult( rule='is_unix_path', value=value,  param=param )
		path_re = r'\/?(\/?.+?)+[\/]?'
		path = re.findall(path_re, value )
		if path:  vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_090"
			vr.err_msg = f"[{value}] is not a unix-style path"
			Validate.log( vr.err_msg , log_err_func)
		return vr 


	#############################################################################################################
	#validation function not found
	@staticmethod
	def is_bool( value, param, log_err_func: Callable =print ):
		vr = ValidateResult( rule='required', value=value,  param=param )
		valid_values = [ True, False, '', None ]
		if value in valid_values:  vr.success= True
		else:
			vr.success = False 
			vr.err_no = "VAL_090"
			vr.err_msg = f"Value [{value}] is not a boolean"
			Validate.log( vr.err_msg , log_err_func)
		return vr 

	@staticmethod
	def log( message, log_err_func: Callable =print ):

		log_err_func( "Validation Failure: " + message )
