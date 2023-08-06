import sys, json

from flask import  render_template, request, send_file,  current_app, session,  abort
from flask_login import current_user,   login_required
from flask_classful import   route 

# from app import myapp, logger  

from zohavi.zwebui import WebUIView
from zohavi.zbase.routes import BaseView 

from . import bp 

class MembersView(BaseView):
	bpname = bp.name
	bp = bp

	##############################################################################################################
	#
	##############################################################################################################
	@route('/membershome', endpoint='membershome')
	# @loggedin_and_ready_user
	def members_home(self):
		logger.debug("** DEF MEMBERS ***")	
		return render_template('_def/base_members.html' )
	 


	##############################################################################################################
	#
	##############################################################################################################
	@route('/memberscontact', endpoint='memberscontact')
	# @loggedin_and_ready_user
	def members_contact(self):
		logger.debug("** DEF MEMBERS ***")	
		return render_template('_def/base_members.html' )
	 

	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/dataget/<viewname>', methods=[ 'GET', 'POST'], endpoint='dataget') 
	# # @loggedin_and_ready_user
	# def data_get(self, viewname):

	# 	(view_item, view_data, lookup_data) = DynamicTableView.read_view_data(viewname)
	# 	# breakpoint()
	# 	if view_item:
	# 		return render_template('_def/table_data.html', view_meta=view_item, view_data=view_data, lookup_data = lookup_data)
	# 	# else:
	# 	logger.error("could not find '{}' in current_app.config['VIEWS']".format(viewname))
	# 	abort(500)




	# ##############################################################################################################
	# #	Delete record
	# ##############################################################################################################
	# @route('/datarem/<viewname>', methods=[  'POST'], endpoint='datarem') 
	# # @loggedin_and_ready_user
	# def data_remove(self, viewname):

	# 	if DynamicTableView.del_view_data(viewname,   request.form ):
	# 		return json.dumps({'success':True}), 200

	# 	return json.dumps({'success':False}), 500

	# ##############################################################################################################
	# #
	# ##############################################################################################################
	# @route('/dataupdate/<viewname>', methods=[ 'POST'], endpoint='dataupdate') 
	# # @loggedin_and_ready_user
	# def data_update(self, viewname):
 		
	# 	rec = DynamicTableView.update_view_data(  viewname, request.form)
	# 	if rec:
	# 		return json.dumps( rec.to_str() ), 200;
	# 	else:
	# 		logger.error('incorrect call {}'.format(viewname))
	# 		abort(500)


