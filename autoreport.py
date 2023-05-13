from flask import Blueprint

autoreport = Blueprint('autoreport', __name__, template_folder='templates', static_folder='static')
