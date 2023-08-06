# import sys, json
import json, pathlib, os, subprocess, re, time


from flask import  render_template, request, send_file, flash, redirect , current_app, session, url_for, abort
# from flask_login import current_user,   login_required
# from flask_security import roles_accepted
from flask_classful import   route 

from app import myapp, logger #,  db 

from . import handler , bp
# from ..common.models import Country

from ..user.handler import   loggedin_and_ready_user
from ..common.commonview import CommonView
# from ..common.common import _
# from ..common.models import ConfigDB
from ..common.dynamic_table_view import DynamicTableView
from ..celery.models import CeleryWorker
from ..processes.models import CommandLineJobArgs


# from ..common.common import _

class CeleryAdminView(CommonView):
	# route_base = '/'
	bpname = bp.name
	

	def __init__(self):
		self.module_name = __name__
 

 # 	##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/manage_jobs/', methods=[ 'GET', 'POST'], endpoint='manage_jobs') 
	# @loggedin_and_ready_user
	# def manage_jobs(self):
	# 	# viewname = 'periodic_background_jobs' 
	# 	# (view_item, view_data, lookup_data) = DynamicTableView.read_view_data(viewname)
	# 	logger.debug('Getting all Jobs')
	# 	all_jobs = JobGroups()
	# 	all_jobs.refresh_status()
	# 	# breakpoint()
	# 	# for job_item in all_jobs.cljg_items:
	# 	# 	pass
	# 	return render_template('_def/manage_jobs.html', all_jobs=all_jobs)



		# breakpoint()


	# @route('/celery_worker_start/ ', methods=[ 'GET', 'POST'], endpoint='celery_worker_start') 
	# def celery_worker_start(self):
		
	# 	# cworker = CeleryWorker.query.filter_by( id = request.form['rec_id'] ).first(); 
	# 	# if not cworker:
	# 	# 	return {'error':f"Failed to find worker {request.form['rec_id']}"},  500, _.CONTENT_TYPE_JSON
	# 	# else:
	# 	# 	if not cworker.active or not self._check_process_running(cworker.pid):
	# 	# 		if self._start_celery_worker_job(cworker):
	# 	# 			myapp.safe_commit()
	# 	# 			return {'success':'true', 'status':'on', 'data':cworker.to_dict()}, 200, _.CONTENT_TYPE_JSON
   
	# 	# return {'error':f"could not start job: {request.form['rec_id']} - worker already active "}, 500, _.CONTENT_TYPE_JSON
	# 	logger.debug('Calling celery worker start')
	# 	# breakpoint()
	# 	pm = ProcessManager(rec_id= request.form['rec_id'] )  
	# 	if pm.start_job():
	# 		return  {'success':True, 'pid': pm.cl_job.pid}, 200, {'ContentType':'application/json'}
	# 	return  {'success':False, 'pid': pm.cl_job.pid}, 500, {'ContentType':'application/json'}


		# if view_item:
			# pm = ProcessManager(process_search_string='CELERY_BEAT')  
			# return render_template('_def/beats_view.html', process_data=pm,  view_meta=view_item, view_data=view_data, lookup_data = lookup_data)

		# abort(500)

 	##############################################################################################################
	#
	##############################################################################################################
	@route('/celery_beats_get/', methods=[ 'GET', 'POST'], endpoint='html_celery_beats_get') 
	@loggedin_and_ready_user
	def html_celery_beats_get(self):
		viewname = 'periodic_background_jobs' 
		(view_item, view_data, lookup_data) = DynamicTableView.read_view_data(viewname)

		if view_item:
			# pm = ProcessManager(process_search_string='CELERY_BEAT') 
			pm=None 
			return render_template('_def/beats_view.html', process_data=pm,  view_meta=view_item, view_data=view_data, lookup_data = lookup_data)

	# 	abort(500)


	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_beats_start/', methods=[ 'GET', 'POST'], endpoint='celery_beats_start') 
	# @loggedin_and_ready_user
	# def celery_beats_start(self):
	# 	# pass	
	# 	logger.debug('Calling celery beats start')
	# 	pm = ProcessManager(process_search_string='CELERY_BEAT')  
	# 	if pm.start_job():
	# 		return  {'success':True, 'pid': pm.cl_job.pid}, 200, {'ContentType':'application/json'}
	# 	return  {'success':False, 'pid': pm.cl_job.pid}, 500, {'ContentType':'application/json'}

	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_beats_stop/', methods=[ 'GET', 'POST'], endpoint='celery_beats_stop') 
	# @loggedin_and_ready_user
	# def celery_beats_stop(self):
	# 	# pass
	# 	logger.debug('Calling celery beats stop')
	# 	pm = ProcessManager(process_search_string='CELERY_BEAT')  
	# 	if pm.stop_job():
	# 		return  {'success':True }, 200, {'ContentType':'application/json'}
	# 	return  {'success':False, 'pid': pm.cl_job.pid}, 500, {'ContentType':'application/json'}


	##############################################################################################################
	#
	##############################################################################################################
	@route('/celery_workers_get/', methods=[ 'GET', 'POST'], endpoint='celery_workers_get') 
	@loggedin_and_ready_user
	def celery_workers_get(self):
		pass

	# 	# -> change to have all jobs on one page.  No need to separate
	# 	# have job in header.
	# 	# have parameters in the bottom section


	# 	# viewname = 'celery_workers'  
	# 	# celery_worker_data = CeleryWorker.query.all() 

	# 	# for celery_worker_rec in celery_worker_data:
	# 	# 	self._update_status_of_job(celery_worker_rec)	#If active, double check status
	# 	# 	logger.debug(f"After updating status - data:{celery_worker_rec.to_str()}"  )
			
	# 	# myapp.safe_commit()
	# 	# celery_worker_data = CeleryWorker.query.all() 
	# 	# return render_template('_def/workers_view.html',  view_data=celery_worker_data ) 
	# 	viewname = 'celery_workers' 
	# 	(view_item, view_data, lookup_data) = DynamicTableView.read_view_data(viewname)

		
	# 	if view_item:
	# 		worker_data = []
	# 		for data_item in view_data:
	# 			pm = ProcessManager(rec_id = data_item['clj_id'])
	# 			worker_hash = {}
	# 			worker_hash['worker_name'] = data_item['worker_name']
	# 			worker_hash['id'] = data_item['clj_id']
	# 			worker_hash['pid'] = pm.cl_job.pid 
	# 			worker_hash['pgid'] = pm.cl_job.pgid 

	# 			for arg in pm.cl_job._args:
	# 				if arg.arg_name == '-l':
	# 					worker_hash['log_level'] = arg.arg_value
	# 				elif arg.arg_name == '--concurrency':
	# 					worker_hash['concurrency_count'] = arg.arg_value
	# 				elif arg.arg_name == '-n':
	# 					worker_hash['worker'] = arg.arg_value
	# 				elif arg.arg_name == '--logfile':
	# 					worker_hash['log_path'] = arg.arg_value
	# 			worker_data.append(worker_hash)  

	# 		logger.debug(worker_data)

	# 			# pm_hash[ data_item['clj_id'] ] = ProcessManager( rec_id = data_item['clj_id'] ) 
	# 		# breakpoint()
	# 		return render_template('_def/workers_view.html', worker_data=worker_data,  view_meta=view_item, view_data=view_data, lookup_data = lookup_data)

	# 	abort(500)

	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_worker_delete/', methods=[ 'GET', 'POST'], endpoint='celery_workers_del') 
	# @loggedin_and_ready_user
	# def celery_worker_delete(self):
	# 	pass
	# # 	# viewname = 'celery_workers' 

	# # 	# cworker = CeleryWorker.query.filter_by( id = request.form['id_worker_rec_id'] ).first()
	# # 	count = CeleryWorker.query.filter_by( id = request.form['rec_id'] ).delete();
	# # 	myapp.safe_commit()

	# # 	if count > 0: return {}, 200, {'ContentType':'application/json'}
	# # 	# logger.debug('delete request')

	# # 	# return render_template('_def/workers_view.html',  view_data=celery_worker_data ) 
	# # 	return {'error':f"Failed to delete reocrd:{request.form['rec_id']}"}, 500, {'ContentType':'application/json'}

	
	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_workers_ge_logs/', methods=[ 'GET', 'POST'], endpoint='celery_workers_get_logs') 
	# @loggedin_and_ready_user
	# def celery_workers_get_logs(self): 
	# 	pass

	# 	cworker_rec = CeleryWorker.query.filter_by( id = request.form['rec_id'] ).first()

	# 	nlines = ""
	# 	if cworker_rec and pathlib.Path( cworker_rec['log_path']  ).is_file():
	# 		nlines = _.run_process_with_output( f"tail -n 20 {cworker_rec['log_path']}" ) 

	# 	# for celery_worker_rec in celery_worker_data:
	# 	# 	self._update_status_of_job(celery_worker_rec)	#If active, double check status
	# 	# 	logger.debug(f"After updating status - data:{celery_worker_rec.to_str()}"  )
			
	# 		# changes_made = True
	# 	# breakpoint()
	# 	# myapp.safe_commit()
	# 	# celery_worker_data = CeleryWorker.query.all() 
	# 	# return render_template('_def/workers_view.html',  view_data=celery_worker_data ) 
	# 	return  {'rec':nlines}, 200, _.CONTENT_TYPE_JSON



	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# # def _generate_process_cl(self, cworker_rec):
	# # 	command_line_partial =	(	f"celery -A app._def.celery.celeryrun worker " 
	# # 								f"-l {cworker_rec['log_level']} "
	# # 								f"--concurrency={cworker_rec['concurrency_count']} "
 # #                     				f"-n {cworker_rec['worker_name']} " )

	# # 	command_line_full = ( 	f"{command_line_partial} "
 # #                     			f"--logfile={cworker_rec['log_path']} "
 # #                     			f"&> {cworker_rec['nohup_path']} & " )
	# # 	return command_line_full, command_line_partial


	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# # def _check_process_running(self, pid):
	# # 	if not pid: return False #no pid given, so not running

	# # 	try:
	# # 		os.kill(int(pid), 0)
	# # 	except OSError:
	# # 		return False
	# # 	return True


	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# # def _update_status_of_job(self, cworker_rec):
	# # 	try:
	# # 		command_full = command_partial = ""
	# # 		command_full, command_partial = self._generate_process_cl( cworker_rec )
			
	# # 		run_check = f"ps -eHjf | egrep '{command_partial}'"	#Check if job ran ok and get the group process id
	# # 		output = _.run_process_with_output(run_check) 
	# # 		r = re.compile( '(\S+)' )

	# # 		for line in output:
	# # 			if line:
	# # 				logger.debug(f"##[{line}]##")
	# # 				item_list = r.findall( str(line) ) 
	# # 				logger.debug(f"Processes created: user:[{item_list[0]}] pid:[{item_list[1]}] ppid:[{item_list[2]}] pgid:[{item_list[3]}]" )
	# # 				# if str_pid != item_list[1] and str_pid != item_list[2]:	#if what we capture is not this running process
	# # 				if item_list[2] == '1': # and item_list[3] == cworker_rec['pgid']:  # main worker thread
	# # 					logger.debug(f'Updating status:{item_list}')
	# # 					cworker_rec.pid  = item_list[1]		#process id of main job
	# # 					cworker_rec.pgid = item_list[3]		#group ID
	# # 					cworker_rec.active = True
	# # 					return
	# # 		cworker_rec.pid  = cworker_rec.pgid = None
	# # 		cworker_rec.active = False
	# # 		# return False
	# # 	except Exception as e:
	# # 		logger.debug(f"Error in running command:{command_full} #error#:{e}" )
	# # 	# return False
	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# # def _start_celery_worker_job(self, cworker_rec):
	# # 	try: 
	# # 		command_full, command_partial = self._generate_process_cl( cworker_rec )
	# # 		logger.debug("worker create command:" + command_full)
	# # 		proc = _.run_process(command_full)
	# # 		logger.debug("process id:" + str(os.getpgid( proc.pid)) )

	# # 		self._update_status_of_job(cworker_rec)
	# # 		return True 	#can skip next records
	# # 	except Exception as e:
	# # 		logger.debug(f"Error in running command:{command_full} #error#:{e}" )
	# # 		cworker_rec.active = False
	# # 		cworker_rec.pid = cworker_rec.pgid = ""

	# # 		return False


	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# # def _stop_celery_worker_job(self, cworker_rec):
	# # 	try:
	# # 		logger.debug(f"Stopping process: [{cworker_rec.to_dict()}]")
	# # 		get_child_process_command = f"ps -f --ppid {cworker_rec['pid']}"
	# # 		output = _.run_process_with_output(get_child_process_command)

	# # 		r = re.compile( '(\S+)' )

	# # 		for line in output:
	# # 			if line:
	# # 				item_list = r.findall( str(line) ) 
	# # 				proc = _.run_process( f"kill -9 {item_list[1]}")	#Kill each child process
	# # 		proc = _.run_process( f"kill -9 { cworker_rec['pid'] }")	#Kill parent 
	# # 		self._update_status_of_job(cworker_rec) 
	# # 		return True
	# # 	except OSError:
	# # 		logger.debug("Error in running command:",command_full ) 
	# # 		return False

	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_worker_start/ ', methods=[ 'GET', 'POST'], endpoint='celery_worker_start') 
	# def celery_worker_start(self):
		
	# 	# cworker = CeleryWorker.query.filter_by( id = request.form['rec_id'] ).first(); 
	# 	# if not cworker:
	# 	# 	return {'error':f"Failed to find worker {request.form['rec_id']}"},  500, _.CONTENT_TYPE_JSON
	# 	# else:
	# 	# 	if not cworker.active or not self._check_process_running(cworker.pid):
	# 	# 		if self._start_celery_worker_job(cworker):
	# 	# 			myapp.safe_commit()
	# 	# 			return {'success':'true', 'status':'on', 'data':cworker.to_dict()}, 200, _.CONTENT_TYPE_JSON
   
	# 	# return {'error':f"could not start job: {request.form['rec_id']} - worker already active "}, 500, _.CONTENT_TYPE_JSON
	# 	logger.debug('Calling celery worker start')
	# 	# breakpoint()
	# 	pm = ProcessManager(rec_id= request.form['rec_id'] )  
	# 	if pm.start_job():
	# 		return  {'success':True, 'pid': pm.cl_job.pid}, 200, {'ContentType':'application/json'}
	# 	return  {'success':False, 'pid': pm.cl_job.pid}, 500, {'ContentType':'application/json'}


	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/celery_worker_stop/ ', methods=[ 'GET', 'POST'], endpoint='celery_worker_stop') 
	# def celery_worker_stop(self):
	# 	# logger.debug('stopping worker')
	# 	# cworker = CeleryWorker.query.filter_by( id = request.form['rec_id'] ).first() 
	# 	# if not cworker:
	# 	# 	return {'error':f"Failed to find worker {request.form['rec_id']}"},  500, _.CONTENT_TYPE_JSON
		 
	# 	# if cworker.active or self._check_process_running(cworker.pid):  
	# 	# 	pgid = cworker['pgid']
	# 	# 	if self._stop_celery_worker_job(cworker): 
	# 	# 		myapp.safe_commit()
	# 	# 		return {'success':'true', 'satus':'off', 'data':cworker.to_dict()}, 200, _.CONTENT_TYPE_JSON
	# 	# 	logger.debug(f'job {pgid} failed to stop')
	# 	# 	return {'error':'could not stop job: {pgid}'}, 500, _.CONTENT_TYPE_JSON
  
	# 	# return {'error': f"could not stop job {request.form['rec_id']} - job not active"}, 500, _.CONTENT_TYPE_JSON
	# 	logger.debug('Calling celery beats stop')
	# 	pm = ProcessManager(rec_id= request.form['rec_id'])  
	# 	if pm.stop_job():
	# 		return  {'success':True }, 200, {'ContentType':'application/json'}
	# 	return  {'success':False, 'pid': pm.cl_job.pid}, 500, {'ContentType':'application/json'}



	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# @route('/background_job_update/', methods=[ 'GET', 'POST'], endpoint='background_job_update') 
	# @loggedin_and_ready_user
	# def background_job_update(self): 
	# 	# pass
	# 	errors = {}

	# 	logger.debug(f"reqeust method [{request.method}]")
	# 	logger.debug(f"reqeust data [{request.form}]")
	# 	# breakpoint()
		
	# 	for item_name in request.form:
	# 		#example key is 'id_job_arg_item_input_99'.  Getting last "_" then extracting id, in this case is 99
	# 		arg_key = item_name[item_name.rfind('_')+1:]	
	# 		arg_obj = myapp.query_orm_to_edit(CommandLineJobArgs).filter_by(id=arg_key).first()
	# 		if arg_obj:
	# 			if arg_obj.arg_type == 'opt':
	# 				arg_obj.clao_id = request.form[item_name ]
	# 			else:
	# 				arg_obj.arg_value = request.form[item_name ] 
	# 		else:
	# 			errors['error'] = f"Failed to find existing arg id: {request.form['item_name']}"
	# 			return errors, 500, _.CONTENT_TYPE_JSON
	# 	if not myapp.safe_commit(): 
	# 		errors['error'] = f"Failed to commit update to job arg updates"
	# 		return errors, 500, _.CONTENT_TYPE_JSON

	# 	return  {  'success': True }, 200, _.CONTENT_TYPE_JSON
		 


	# # ##############################################################################################################
	# # #
	# # ##############################################################################################################
	# @route('/celery_worker_update/', methods=[ 'GET', 'POST'], endpoint='celery_worker_update') 
	# @loggedin_and_ready_user
	# def celery_worker_update(self): 
	# 	pass
	# 	errors = {}

	# 	logger.debug(f"reqeust method [{request.method}]")
	# 	logger.debug(f"reqeust data [{request.form}]")

	# 	if not _.is_dir_valid( request.form['id_log_file_path'])  		: errors['id_log_file_path'] = 'Invalid path'
	# 	if not _.is_dir_valid( request.form['id_process_output_path']) 	: errors['id_process_output_path'] = 'Invalid path'

	# 	cworker = None 
	# 	# breakpoint()
	# 	if not errors:	#No errors found
	# 		if request.form.get('id_worker_rec_id'):	#If found and not blank
	# 			cworker = CeleryWorker.query.filter_by( id = request.form['id_worker_rec_id'] ).first()
	# 			if cworker:
	# 				cworker.worker_name  = request.form['id_worker_name']
	# 				# cworker._job()
	# 				# cworker.log_path =request.form['id_log_file_path']
	# 				# cworker.log_level = request.form['id_log_level']
	# 				# cworker.nohup_path = request.form['id_process_output_path']
	# 				# cworker.concurrency_count = request.form['id_concurrent_process_count']
	# 				# cworker.pid = ''
	# 				# cworker.active = False
	# 				# if myapp.safe_commit(cworker): return cworker.to_json(), 200, _.CONTENT_TYPE_JSON
	# 				# errors['error'] = f"Failed to commit update to existing record id: {request.form['id_worker_rec_id']}"
	# 			else:
	# 				errors['error'] = f"Failed to find existing record id: {request.form['id_worker_rec_id']}"

	# 		else:	#this is new worker
	# 			cworker = CeleryWorker( worker_name = request.form['id_worker_name'], active=False)

	# 			# breakpoint()
	# 			if myapp.safe_add_and_commit(cworker): return cworker.to_json(), 200, _.CONTENT_TYPE_JSON
	# 			errors['error'] = f"Failed to create new record"
		
	# 	logger.error(errors)
	# 	return json.dumps( errors ), 500, _.CONTENT_TYPE_JSON

 # 