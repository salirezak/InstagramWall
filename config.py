import os


class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')

class Development(Config):
    DEBUG=True
    TESTING=True

class Production(Config):
    DEBUG=False
    TESTING=False