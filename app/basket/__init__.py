from flask import Blueprint

bp = Blueprint('basket', __name__, template_folder='templates')

from app.basket import routes
