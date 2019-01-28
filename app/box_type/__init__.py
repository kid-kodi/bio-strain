from flask import Blueprint

bp = Blueprint('box_type', __name__, template_folder='templates')

from app.box_type import routes
