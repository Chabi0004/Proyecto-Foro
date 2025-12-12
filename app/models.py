# app/models.py
from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# Tabla de asociación para suscripciones (muchos a muchos)
subscriptions = db.Table(
    'subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topics.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relaciones
    topics = db.relationship('Topic', backref='author', lazy=True, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")
    subscribed_topics = db.relationship(
        'Topic',
        secondary=subscriptions,
        lazy='subquery',
        backref=db.backref('subscribers', lazy=True)
    )

    def __repr__(self):
        return f'<User {self.username}>'

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    topics = db.relationship('Topic', backref='section', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Section {self.title}>'

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    posts = db.relationship('Post', backref='topic', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Topic {self.title}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))