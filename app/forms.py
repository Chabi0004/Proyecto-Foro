# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está en uso.')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class TopicForm(FlaskForm):
    title = StringField('Título del Tema', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Contenido Inicial', validators=[DataRequired()])
    submit = SubmitField('Crear Tema')

class PostForm(FlaskForm):
    content = TextAreaField('Tu Respuesta', validators=[DataRequired()])
    submit = SubmitField('Publicar Respuesta')

class SectionForm(FlaskForm):
    title = StringField('Título de la Sección', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Descripción (Opcional)')
    submit = SubmitField('Crear Sección')