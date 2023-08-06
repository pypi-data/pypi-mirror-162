from flask import Blueprint

bp = Blueprint('webui', __name__, template_folder='templates', static_folder='static', static_url_path='/static') 


from .routes import WebUIView
