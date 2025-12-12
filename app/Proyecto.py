# ... (imports anteriores) ...
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def send_daily_summary_job():
    """Función que se ejecutará diariamente. Crea un contexto de app para operar."""
    with app.app_context():
        from app.email import send_daily_summary
        print("Ejecutando tarea programada: Enviar resumen diario...")
        send_daily_summary()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    # Importar y registrar las rutas
    from . import routes
    app.register_blueprint(routes.bp)

    # Programar la tarea diaria
    scheduler = BackgroundScheduler()
    # Ejecuta todos los días a las 08:00 AM (ajusta la hora según necesites)
    scheduler.add_job(func=send_daily_summary_job, trigger="cron", hour=8, minute=0, id='daily_summary_job')
    scheduler.start()
    
    # Asegurarse de que el scheduler se cierre al salir de la app
    atexit.register(lambda: scheduler.shutdown())

    # Crear las tablas si no existen (para desarrollo)
    with app.app_context():
        db.create_all()

    return app
    # ... (imports y rutas anteriores sin cambios) ...

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

# ... (rutas de perfil y admin) ...

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

    from flask import current_app as app, render_template # CORRECCIÓN: Añadido render_template
from flask_mail import Message
from .models import User, Topic, Post
from datetime import datetime, timedelta

def send_daily_summary():
    users = User.query.filter(User.subscribed_topics.any()).all()
    if not users:
        print("No hay usuarios con suscripciones a los que enviar resumen.")
        return

    yesterday = datetime.utcnow() - timedelta(days=1)

    for user in users:
        # MEJORA: Obtener IDs de temas suscritos para una consulta más eficiente
        subscribed_topic_ids = [t.id for t in user.subscribed_topics]
        if not subscribed_topic_ids:
            continue

        # MEJORA: Una sola consulta para obtener todos los nuevos posts de los temas suscritos
        new_posts = Post.query.filter(
            Post.topic_id.in_(subscribed_topic_ids),
            Post.date_created >= yesterday
        ).order_by(Post.date_created.desc()).all()

        if not new_posts:
            continue # No enviar email si no hay actividad

        # Agrupar posts por tema para una mejor visualización
        posts_by_topic = {}
        for post in new_posts:
            if post.topic not in posts_by_topic:
                posts_by_topic[post.topic] = []
            posts_by_topic[post.topic].append(post)

        subject = "Tu Resumen Diario del Foro"
        body_html = render_template('daily_summary_email.html', name=user.username, posts_by_topic=posts_by_topic)
        
        msg = Message(
            subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        msg.html = body_html
        
        try:
            app.mail.send(msg)
            print(f"Resumen enviado a {user.email}")
        except Exception as e:
            print(f"Error al enviar email a {user.email}: {e}")

from app.models import User, Section
from werkzeug.security import generate_password_hash
db.drop_all() # Opcional: para empezar desde cero
db.create_all()
admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('adminpassword', method='sha256'), is_admin=True)
db.session.add(admin)
general = Section(title='General', description='Temas de conversación general.')
db.session.add(general)
db.session.commit()
exit()