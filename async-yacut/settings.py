import os


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        os.getenv('SQLALCHEMY_DATABASE_URI'),
    )
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG')
    TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER', '../html/templates')
    STATIC_FOLDER = os.getenv('STATIC_FOLDER', '../html')
