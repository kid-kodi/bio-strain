from flask import Blueprint

bp = Blueprint('rack', __name__, template_folder="templates")

from app.rack import routes
