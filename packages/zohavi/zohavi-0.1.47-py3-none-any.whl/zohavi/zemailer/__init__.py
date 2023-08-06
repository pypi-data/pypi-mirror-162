from flask import Blueprint
from .emailer import Emailer

bp = Blueprint('email', __name__, template_folder='templates')



