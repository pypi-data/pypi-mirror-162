from ..celery.models import CeleryWorker
from app import myapp


def add_worker(worker_name, app_name, log_path='', concurrency = 2, active=True):
	cw = CeleryWorker()

	cw.worker_name = worker_name
	cw.app_name = app_name
	cw.log_path  = log_path
	cw.concurrency = concurrency
	cw.active = active	 

	myapp.db.session.add(cw) 
	myapp.db.session.commit() 


# class CeleryWorker(db.Model,  TableDefault):
# 	#typical execution of celery script
# 	#celery -A app._def.celery.celeryrun worker -l INFO --concurrency=2 -n worker1 --logfile=~/prj/saast/dev/logs/cworker1.log
# 	__tablename__ = 'sys_celery_worker' 
# 	id = db.Column(db.Integer(), primary_key=True)
# 	worker_name = db.Column(db.String(100) )
# 	app_name = db.Column(db.String(100) )
# 	log_path = db.Column(db.String(100) )
# 	concurrency = db.Column(db.Integer(1) ) 
# 	active = db.Column(db.Boolean() , default=True)
