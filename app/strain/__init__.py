from flask import Blueprint

bp = Blueprint('strain', __name__, template_folder="templates")

from . import routes