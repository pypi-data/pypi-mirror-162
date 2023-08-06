
from zohavi.zbase.routes import BaseView
from . import bp

class WebUIView(BaseView):
	# route_base = '/'
	bpname = 'webui'
	bp = bp