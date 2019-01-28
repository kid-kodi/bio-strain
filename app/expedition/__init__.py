from flask import Blueprint

bp = Blueprint('expedition', __name__, template_folder='templates')

from app.expedition import routes
