from flask import Blueprint

bp = Blueprint('equipment_type', __name__, template_folder='templates')

from app.equipment_type import routes
