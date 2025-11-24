from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(
    __name__,
    template_folder=Config.TEMPLATE_FOLDER,
    static_folder=Config.STATIC_FOLDER,
)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import views, models, forms, api_views
