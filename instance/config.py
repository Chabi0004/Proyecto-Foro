# instance/config.py
import os

SECRET_KEY = 'Javier2004.'

# Configuración para MySQL (XAMPP)
DB_USER = 'foro_user'
DB_PASS = 'Admin12345'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'foro_db'

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración de correo (Gmail)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'tu-email@gmail.com'
MAIL_PASSWORD = 'tu-contrasena-de-aplicacion' 
MAIL_DEFAULT_SENDER = 'tu-email@gmail.com'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://foro_user:Admin12345@localhost:3306/foro_db'