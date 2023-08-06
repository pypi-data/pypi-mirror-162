import unittest
unittest.TestLoader.sortTestMethodsUsing = None

from pathlib import Path 
import sys, os, jsoncfg, json
sys.path.insert(0, '../../../')


from zohavi.zwebui.jinja_cust_funcs import JCFunc


class TestCore(unittest.TestCase):

	########################################################################
	# Test
	def test_0010_defaulter(self):
		# jc = JCFunc()

		value = JCFunc.defaulter( 'abc', 'def')
		self.assertEqual(  value , 'abc')
 		
		value = JCFunc.defaulter( None, 'def')
		self.assertEqual(  value , 'def')

		value = JCFunc.defaulter( '', 'def')
		self.assertEqual(  value , 'def')

	########################################################################
	# Test
	def test_0020_dict_to_json_str(self):
		dict_out = {'name':'john', 'address':'NY', 'age':22, 'gender':'M'}

		json_str = JCFunc.dict_to_json_str( dict_out , ['apple'] )
		self.assertEqual(  json_str , '{}' )

		json_str = JCFunc.dict_to_json_str( dict_out , ['name'] )
		self.assertEqual(  json_str , '{"name": "john"}' )
 		

		json_str = JCFunc.dict_to_json_str( dict_out , ['name', 'age'] )
		self.assertEqual(  json_str , '{"name": "john", "age": 22}' )
 		
	########################################################################
	# Test
	def test_0030_list_dict_to_json_str(self):
		dict_out = [ {'name':'john', 'address':'NY', 'age':22, 'gender':'M'},
					 {'name':'jill', 'address':'HK', 'age':44, 'gender':'F'},
					 {'name':'jack', 'address':'CN', 'age':14, 'gender':'M'} ]

		json_str = JCFunc.list_dict_to_json_str( dict_out , ['name'] )
		self.assertEqual(  json_str , '[{"name": "john"}, {"name": "jill"}, {"name": "jack"}]' )
 		
		json_str = JCFunc.list_dict_to_json_str( dict_out , ['name', 'age'] )
		self.assertEqual(  json_str , '[{"name": "john", "age": 22}, {"name": "jill", "age": 44}, {"name": "jack", "age": 14}]' )
 		
		json_str = JCFunc.list_dict_to_json_str( dict_out , ['apple'] )
		self.assertEqual(  json_str , '[]' )
 		
 		

if __name__ == '__main__':
    unittest.main()