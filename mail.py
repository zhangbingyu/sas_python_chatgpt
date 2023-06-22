from app import app, email
from flask_mail import Message

# @app.route("/sendmail")
def send_mail(recipient, subject, message):
    msg = Message(subject=subject, sender='contact@themodeladvantage.com',
                recipients=[recipient])
    msg.body = message
    email.send(msg)
    return "Done. Please check your email for instructions."
