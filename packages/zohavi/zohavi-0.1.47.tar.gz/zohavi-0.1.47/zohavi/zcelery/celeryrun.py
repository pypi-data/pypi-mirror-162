# from time import sleep 
from celery import Celery, Task


from app import myapp, logger
from .models import CeleryBeatJobs
from ..processes.process_manager import JobItem
from flask_sqlalchemy import SQLAlchemy

####setup celery scheduler
celeryJob = Celery('cjob' )
celeryJob.config_from_object('config.config_main.ConfigCeleryDev')

#####
# worker: -> called with subprocess
# beats: -> run as separate task, but then task uses same connection
class DatabaseTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SQLAlchemy(myapp.app)
        return self._db


@celeryJob.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	celery_job_list = CeleryBeatJobs.query.all()

	for celery_job in celery_job_list:
		logger.debug(f"Registering auto: {celery_job.beat_name}")
		sender.add_periodic_task( celery_job.frequency , run_external_task.s( celery_job.clj_id ), name=celery_job.beat_name )

@celeryJob.task(base=DatabaseTask, name="cjob.run_external_task")
def run_external_task(job_id):
	logger.debug(f"Running celery job: [{job_id}]")
	# myapp.db.engine.dispose() 
	# logger.debug(f"disposed conectino")
	job_recs = run_external_task.db.session.query(CeleryBeatJobs).all()
	for job in job_recs:
		logger.debug(f"Records:{job.to_str()}")
	logger.debug(f"Loop done")
	pm = JobItem(job_id = job_id)
	logger.debug(f"Job starting")
	pm.start_job(new_session=False, wait_until_finish=True)
	logger.debug(f"Job done")
# def register_beat(job_name, args):


# @celeryJob.on_after_configure.connect
def register_periodic_tasks():
	# logger.debug(f"Running celery job: [{job_id}]")
	celery_job_list = CeleryBeatJobs.query.all()

	jobs = {}
	for celery_job in celery_job_list:
		logger.debug(f"Registering force: {celery_job.beat_name}")
		jobs[ celery_job.beat_name ] = { 'task': 'cjob.run_external_task', 'args': (celery_job.clj_id), 'schedule': celery_job.frequency }

	if jobs: celeryJob.conf.beat_schedule = jobs

if __name__ == '__main__':
# logger.debug(f"Running: [{__name__}]")
	register_periodic_tasks()

# 	# myapp.delete_table( CeleryBeatJobTypeArgs, commit=False )  
# 	# myapp.delete_table( CeleryBeatJobType, commit=True )  
# 	# for arg in CeleryBeatJobTypeArgs.query.all():
# 	# 	arg.delete()
# 	try:
# 		# item_count = CeleryBeatJobType.query.filter_by(job_name=job_name).delete()	#delete any existing records with the same entries
# 		# if item_count > 0: myapp.safe_commit()
# 		# job = CeleryBeatJobType(job_name=job_name)
# 		# for arg in args:
# 		# 	logger.debug('*#* running once')
# 		# 	# job.args.append( CeleryBeatJobTypeArgs(arg_name = arg['arg_name'], arg_type = arg['arg_type']) )

# 		# myapp.safe_add_and_commit(job)
# 		pass
# 	except Exception as e:
# 		logger.error('Error on delete:' + str(e)) 



# def register_beat

# #############################################################################
# # Generic task to run any function under celery dynamically
# #############################################################################
# @celeryJob.task
# def celery_run_func(module_name, func_name, **kwargs): 

# 	try:
# 		logger.info("A:{}".format(module_name))
# 		mod = __import__(module_name, fromlist=[ func_name ]) 
 
# 		func = getattr(mod, func_name) 
		
# 		logger.info("calling [{}] [{}] as [{}]".format(module_name, func_name, str(func)))
# 		return func( **kwargs)

# 	except:
# 		e = sys.exc_info()[0]
# 		logger.info("ERROR:{}".format(e))

# #############################################################################
# # Test job
# #############################################################################
# @celeryJob.task(name="cjob.jobtest")
# def celerey_job_test(nSec):
# 	logger.info("*#*: Testing celery job - start - sleep for {} seconds".format(nSec))
# 	sleep(nSec)
# 	logger.info("*#*: Job done")
# 	return True

# #############################################################################
# # Test job
# #############################################################################
# @celeryJob.task(name="cjob.ext_run")
# def celerey_run_external_script(beat_id):
# 	logger.info("*#*: Testing celery job - start - sleep for {} seconds".format(nSec))
# 	sleep(nSec)
# 	logger.info("*#*: Job done")
# 	return True

# celeryJob.conf.beat_schedule = {
#     'heart-beat-check-every-5-mins': {
#         'task': 'cjob.jobtest',
#         'schedule': 300.0,		#run every 300 seconds
#         'args': [2]			#sleep for 2 seconds
#     }
# }