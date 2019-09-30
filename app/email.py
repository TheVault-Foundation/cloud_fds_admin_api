from app.extensions import mail
from flask_mail import Message
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.msgId = msg.msgId.split('@')[0] + '@short_string'
    msg.html = html_body
    from manage import app
    Thread(target=send_async_email, args=(app, msg)).start()
