# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Section, Topic, Post
from .forms import LoginForm, RegistrationForm, TopicForm, PostForm, SectionForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    sections = Section.query.order_by(Section.title).all()
    return render_template('index.html', sections=sections)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Inicio de sesión fallido. Por favor, comprueba usuario y contraseña.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/section/<int:section_id>')
def section(section_id):
    section_obj = Section.query.get_or_404(section_id)
    return render_template('section.html', section=section_obj)

@bp.route('/section/<int:section_id>/new_topic', methods=['GET', 'POST'])
@login_required
def create_topic(section_id):
    section_obj = Section.query.get_or_404(section_id)
    form = TopicForm()
    if form.validate_on_submit():
        new_topic = Topic(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            section_id=section_obj.id
        )
        db.session.add(new_topic)
        db.session.commit()
        flash('¡Tu tema ha sido creado!', 'success')
        return redirect(url_for('main.topic', topic_id=new_topic.id))
    return render_template('new_topic.html', form=form, section=section_obj)

@bp.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    topic_obj = Topic.query.get_or_404(topic_id)
    form = PostForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        new_post = Post(
            content=form.content.data,
            user_id=current_user.id,
            topic_id=topic_obj.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Tu respuesta ha sido publicada.', 'success')
        return redirect(url_for('main.topic', topic_id=topic_id))
    
    is_subscribed = current_user.is_authenticated and topic_obj in current_user.subscribed_topics
    return render_template('topic.html', topic=topic_obj, form=form, is_subscribed=is_subscribed)

@bp.route('/subscribe/<int:topic_id>', methods=['POST'])
@login_required
def subscribe(topic_id):
    topic_obj = Topic.query.get_or_404(topic_id)
    if topic_obj in current_user.subscribed_topics:
        current_user.subscribed_topics.remove(topic_obj)
        flash('Te has desuscrito del tema.', 'info')
    else:
        current_user.subscribed_topics.append(topic_obj)
        flash('Te has suscrito al tema. Recibirás un resumen diario de la actividad.', 'success')
    db.session.commit()
    return redirect(url_for('main.topic', topic_id=topic_id))

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', subscribed_topics=current_user.subscribed_topics)

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    form = SectionForm()
    if form.validate_on_submit():
        new_section = Section(title=form.title.data, description=form.description.data)
        db.session.add(new_section)
        db.session.commit()
        flash('Sección creada exitosamente.', 'success')
        return redirect(url_for('main.admin'))
        
    sections = Section.query.order_by(Section.title).all()
    return render_template('admin.html', form=form, sections=sections)