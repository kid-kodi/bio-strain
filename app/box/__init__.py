from flask import Blueprint

bp = Blueprint('box', __name__, template_folder="templates")

from app.box import routes
