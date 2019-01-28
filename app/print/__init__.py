from flask import Blueprint

bp = Blueprint('print', __name__, template_folder='templates')

from app.print import routes
