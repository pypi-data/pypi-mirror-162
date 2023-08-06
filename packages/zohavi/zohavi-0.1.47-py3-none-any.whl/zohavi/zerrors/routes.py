
from flask import  render_template, request  
# from flask_classful import   route

# from app import myapp, logger #,  db 
from . import bp  
from zohavi.zbase import BaseView
 

class ErrorsView(BaseView):
	# route_base = '/'
	bpname = bp.name
	bp = bp
	
@bp.app_errorhandler(404)
def not_found_error(error):
	# logger.debug('404 page not found for:{}'.format(request.url))
	return render_template('zerrors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
	# myapp.db.session.rollback()
	return render_template('zerrors/500.html'), 500
