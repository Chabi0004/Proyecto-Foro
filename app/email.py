# app/email.py
from flask import current_app, render_template
from flask_mail import Message
from .models import User, Topic, Post
from datetime import datetime, timedelta

def send_daily_summary():
    with current_app.app_context():
        users = User.query.filter(User.subscribed_topics.any()).all()
        if not users:
            print("No hay usuarios con suscripciones.")
            return

        yesterday = datetime.utcnow() - timedelta(days=1)

        for user in users:
            subscribed_topic_ids = [t.id for t in user.subscribed_topics]
            if not subscribed_topic_ids:
                continue

            new_posts = Post.query.filter(
                Post.topic_id.in_(subscribed_topic_ids),
                Post.date_created >= yesterday
            ).order_by(Post.date_created.desc()).all()

            if not new_posts:
                continue

            posts_by_topic = {}
            for post in new_posts:
                if post.topic not in posts_by_topic:
                    posts_by_topic[post.topic] = []
                posts_by_topic[post.topic].append(post)

            subject = "Tu Resumen Diario del Foro"
            body_html = render_template('daily_summary_email.html', name=user.username, posts_by_topic=posts_by_topic)
            
            msg = Message(
                subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            msg.html = body_html
            
            try:
                current_app.mail.send(msg)
                print(f" Resumen enviado a {user.email}")
            except Exception as e:
                print(f" Error al enviar email a {user.email}: {e}")