from flask import Blueprint

bp = Blueprint('equipment', __name__, template_folder="templates")

from app.equipment import routes
