from flask import Blueprint

bp = Blueprint('strain_type', __name__, template_folder="templates")

from . import routes