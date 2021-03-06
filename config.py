import os
# from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(basedir, '.flaskenv')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or \
    os.path.join(basedir, 'app', 'static', 'upload')
    IMAGES = os.environ.get('IMAGES')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS')
    ADMINS = os.environ.get('ADMINS')
    MAX_CONTENT_LENGHT = os.environ.get('MAX_CONTENT_LENGHT')
    POST_PER_PAGE = int(os.environ.get('POST_PER_PAGE'))
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')