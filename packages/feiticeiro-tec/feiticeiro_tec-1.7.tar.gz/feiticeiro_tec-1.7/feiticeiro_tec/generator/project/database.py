from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from ..database import models
def init_app(app):
    db.init_app(app)
