from flask import Blueprint

bp = Blueprint('store', __name__, template_folder='templates')

from app.store import routes
