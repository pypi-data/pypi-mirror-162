import  datetime, pytz , pathlib, re, subprocess

 
class Utils(object):
	CONTENT_TYPE_JSON = {'ContentType':'application/json'}
	

	################################################################################################
	# Get currnt datetime
	@staticmethod
	def run_process_with_output(command, working_dir=None, wait_until_finish=False):
		try:
			# breakpoint()
			# with myapp.app.app_context():
			# base_dir = working_dir if working_dir else current_app.config['BASE_DIR']
			# logger.debug(f"Running command:[{command}] under dir: [{base_dir}]") 
			# proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd = base_dir)
			proc = subprocess.Popen(command, shell=True, cwd = working_dir, stdout=subprocess.PIPE )
			# breakpoint()
			output = proc.communicate()[0].decode().split('\n') 	#Get the jobs output
			if wait_until_finish: p_status = proc.wait()
			
			return output
		except Exception as e:
			print(f"Error in running command:{command} #error#:{e}")
			return None
			# logger.debug(f"Error in running command:{command} #error#:{e}" )

	################################################################################################
	# Get currnt datetime
	@staticmethod
	def run_process(command, new_session=True, working_dir=None, wait_until_finish=False):
		# breakpoint()
		try:	 
			command_list =  command  
			print(f"Running command:[{command_list}] under dir: [{working_dir}]")  
			proc = subprocess.Popen(command_list, shell=True, start_new_session=True ,  cwd = working_dir  ) #, stdout=subprocess.PIPE)   
			if wait_until_finish:  p_status = proc.wait() 
			# breakpoint()
			return proc
		except Exception as e:
			print(f"Error in running command:{command_list} #error#:{e}")
			return None
			# logger.debug(f"Error in running command:{command} #error#:{e}" )


	################################################################################################
	# Get currnt datetime
	@staticmethod
	def get_datetime_now(timezone='UTC'):
		return datetime.datetime.now(pytz.timezone( timezone ))

	################################################################################################
	# Check if regex is inside a string
	@staticmethod
	def get_datetime_str(dateObj):
		return dateObj.strftime("%Y-%m-%d %H:%M")

	################################################################################################
	# Check if regex is inside a string
	@staticmethod
	def get_date_str(dateObj):
		return dateObj.strftime("%Y-%m-%d")


	################################################################################################
	# Check if file or path is valid
	@staticmethod
	def is_dir_valid(file_path_arg):
		if Utils.is_file_or_dir(file_path_arg ): return True
		curr_path = pathlib.Path( file_path_arg)
		if curr_path.parents[0].is_dir(): return True #If file is not valid but path is ok
		return False
		 

	################################################################################################
	# Check if path is valid only
	@staticmethod
	def is_file_or_dir(file_path_args):
		return pathlib.Path( file_path_args  ).is_file() or  pathlib.Path( file_path_args  ).is_dir()

 
	################################################################################################
	# Convert date from YYYY-MM-DD to a date object
	@staticmethod
	def date_str_to_date_obj(  dateStr ):
		# logger.info("dateStr =[{}]".format(dateStr))
		if re.search('\d\d\d\d-\d\d-\d\d', dateStr):
			return datetime.datetime.strptime( dateStr + " 12:00AM", "%Y-%m-%d %I:%M%p" )
		return None 

	@staticmethod
	def is_all_from_listA_in_listB(  listA, listB):
		for item in listA:
			if item not in listB: return False
		return True

	@staticmethod
	def has_all_dict_values(value_list, dict_obj):
		for item in value_list:
			if not dict_obj.get(item, False): return False
		return True

	
	####################################################################################################################################
	# add two directories together regardless of directoy one having a trailing '/'
	@staticmethod
	def concat_dirs(base_dir, *sub_dirs):
		# breakpoint()
		new_dir = base_dir;
		for curr_sub_dir in sub_dirs :
			if curr_sub_dir:
				# logger.debug(f"adding {new_dir} + {curr_sub_dir} ")
				add_sub_dir = curr_sub_dir	
				if curr_sub_dir[0] == '/': curr_sub_dir = curr_sub_dir[1:]

				if new_dir[-1] == "/": 
					new_dir += curr_sub_dir
				else:  
					new_dir += "/" + curr_sub_dir
		if new_dir and new_dir[-1] != "/":
			new_dir += "/"

		# logger.debug("returning adding:" + new_dir)
		return new_dir

