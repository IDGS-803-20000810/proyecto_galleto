import os
from sqlalchemy import create_engine
import urllib

class Config(object):
    SECRET_KEY='Clave_Nueva'
    SESSION_COOKIE_SECURE=False
    RECAPTCHA_PUBLIC_KEY = "6LdoUpQpAAAAAHMJhflBg6gi6L04IfBw82xK5V5_"
    RECAPTCHA_PRIVATE_KEY= "6LdoUpQpAAAAADCpDA8zxCWCF3OsGz3PG-SsoKIe"


class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://javier:root@localhost/seguridadInformatica'
    SQLALCHEMY_TRACK_MODIFICATIONS=False