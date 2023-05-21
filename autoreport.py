from flask import Blueprint, Flask

autoreport = Blueprint('autoreport', __name__, template_folder='templates', static_folder='static')
app = Flask(__name__, template_folder='templates/autoreport')
