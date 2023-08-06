# from sqlalchemy.orm import relationship


from app import myapp

from zohavi_base_model.models import TableDefault
db = myapp.db

############################################################################################################
############################################################################################################
class CeleryWorker(db.Model,  TableDefault):
	__tablename__ = 'sys_celery_worker' 
	id = db.Column(db.Integer(), primary_key=True)
	worker_name = db.Column(db.String(100) ) 
	clj_id = db.Column(db.Integer(), db.ForeignKey( 'sys_cl_job.id'  , ondelete='CASCADE' ) )
	_job = db.relationship('CommandLineJob', backref='sys_celery_worker')
	#log_path = db.Column(db.String(255) )
	#log_level = db.Column(db.String(10) ) 
	#nohup_path = db.Column(db.String(255) )
	#concurrency_count = db.Column(db.Integer() ) 
	#pid = db.Column(db.String(10) ) 
	#pgid = db.Column(db.String(10) ) 
	active = db.Column(db.Boolean() , default=True)

############################################################################################################
############################################################################################################
class CeleryBeatJobs(db.Model,  TableDefault):
	__tablename__ = 'sys_beat_config' 
	id = db.Column(db.Integer(), primary_key=True)
	beat_name = db.Column(db.String(100), unique=True)
	clj_id = db.Column(db.Integer(), db.ForeignKey( 'sys_cl_job.id'  , ondelete='CASCADE' ) )
	_job = db.relationship('CommandLineJob', backref='sys_beat_config')
	frequency = db.Column(db.Integer() )
	args_string = db.Column(db.String(100) ) 
	active = db.Column(db.Boolean() , default=True)


# ############################################################################################################
# ############################################################################################################
# class CeleryBeatJobTypeArgs(db.Model, TableDefault):
# 	__tablename__ = 'sys_celery_beat_job_args'
# 	id = db.Column(db.Integer(), primary_key=True)
# 	job_id = db.Column(db.Integer(), db.ForeignKey( 'sys_celery_beat_job.id'  , ondelete='CASCADE') )
# 	# job_id = db.Column(db.Integer(), db.ForeignKey( CeleryBeatJobType.id  ) )
# 	# parent = db.relationship(CeleryBeatJobType, backref=db.backref("child", cascade="all,delete"))
# 	arg_name = db.Column(db.String(100) ) 
# 	arg_type = db.Column(db.String(20) ) 
# ############################################################################################################
# ############################################################################################################
# class CeleryBeatJobType(db.Model, TableDefault):
# 	__tablename__ = 'sys_celery_beat_job'
# 	id = db.Column(db.Integer(), primary_key=True)
# 	job_name = db.Column(db.String(100) ) 
# 	args = db.relationship(CeleryBeatJobTypeArgs,  backref="sys_celery_beat_job", passive_deletes=True)
# 	# child = db.relationship("CeleryBeatJobTypeArgs",  backref="sys_celery_beat_job", cascade="all,delete-orphan")
# 	# backref=backref("items", cascade="all, delete-orphan")

