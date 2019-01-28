from flask import Blueprint

bp = Blueprint('phenotype', __name__, template_folder="templates")

from . import routes