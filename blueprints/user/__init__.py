from flask import Blueprint

user = Blueprint('user', __name__, url_prefix='/')

from . import views, models