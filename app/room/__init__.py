from flask import Blueprint

bp = Blueprint('room', __name__, template_folder="templates")

from app.room import routes
