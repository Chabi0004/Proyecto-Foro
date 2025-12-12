# init_db.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
# Importa TODOS los modelos para que SQLAlchemy los conozca
from app.models import User, Section, Topic, Post

app = create_app()

with app.app_context():
    db.drop_all()  # opcional: para empezar limpio
    db.create_all()
    print("Tablas creadas correctamente.")