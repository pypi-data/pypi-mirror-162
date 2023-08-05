from flask import Flask
import os
from flask_cors import CORS

class Servidor():
    pasta = os.path.dirname(__file__)

    def config(self):
        self._app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI','sqlite:///database.db')
        self._app.config['CORS_HEADERS'] = 'Content-Type'
        self._app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self._app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'SECRET_KEY')

    def ext(self):
        from {project_name} import database, blueprints
        database.init_app(self._app)
        blueprints.init_app(self._app)
        CORS(self._app, origins='*', supports_credentials=True)

    @property
    def app(self):
        self._app = Flask(__name__)
        self.config()
        self.ext()
        return self._app

    def run(self, *args, **kw):
        return self.app().run(*args, **kw)
