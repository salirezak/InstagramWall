from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/')

from . import models
from . import views, accounts_views