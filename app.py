from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from config import Development, Production


app = Flask(__name__)
app.config.from_object(Production)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)

from blueprints.admin import admin
from blueprints.user import user

app.register_blueprint(admin)
app.register_blueprint(user)