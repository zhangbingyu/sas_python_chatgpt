from flask_mail import Message

from app import email


# @app.route("/sendmail")
def send_mail(recipient, subject, message):
    """send emails"""
    msg = Message(subject=subject,
                recipients=[recipient])
    msg.html = message
    email.send(msg)
    return "Done. Please check your email for instructions."
