from datetime import datetime, timedelta, timezone
from flask import redirect, render_template, request, flash, get_flashed_messages, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
import jwt

from app import app, db, login_manager
from forms import RegistrationForm, LoginForm, ResetInitialForm, ResetForm
from models import User
from mail import send_mail
import sasai

@app.route("/register", methods=['GET', 'POST'])
def register():
    """user register"""
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template("register.html", form=form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            active=True,
            username=form.username.data,
            credit=10
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Welcome {user.username}, you are signed up. You have ten free attempts")
        return render_template("message.html", messages=get_flashed_messages(), redirect_url=url_for("home"))
    return render_template("register.html", form=form)

@login_manager.user_loader
def load_user(user_id):
    """load user required by flask-login"""
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    """user login"""
    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", form=form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_url = request.args.get('next')
            # url_has_allowed_host_and_scheme should check if the url is safe
            # TODO: implement url_has_allowed_host_and_scheme
            return redirect(next_url or url_for("home"))
        else:
            flash("Email or Password does not match our record.")
            return render_template("login.html", form=form, messages=get_flashed_messages())
    else:
        return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    """user logout"""
    logout_user()
    return redirect(url_for("home"))

@app.route("/forgotpwd", methods=["GET", "POST"])
def forgot_password():
    """send password reset link"""
    form = ResetInitialForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # generate reset token
            token = generate_jwt_token(user)
            message = f"""
                Please click this <a href="{url_for('reset', token=token, _external=True)}">link</a> to reset your password.
                The link expires after 5 minutes.
            """
            topic = "Password Reset"
            recipient = user.email
            # send an email to user.email
            send_mail(recipient, topic, message)
            flash(f"Email has been sent to {user.email}. Follow the instructions.")
            return render_template("message.html", messages=get_flashed_messages(),
                                   redirect_url=url_for("login", _external=True))
        flash(f"{form.email.data} does not exist.")
        return render_template("forgot_password.html", messages=get_flashed_messages())
    return render_template("forgot_password.html", form=form)

@app.route("/reset", methods=["GET", "POST"])
def reset():
    """reset password"""
    token = request.args.get("token", None)
    if not token:
        flash("Request reset link first")
        return render_template("message.html", messages=get_flashed_messages(),
                               redirect_url = url_for("forgot_password"))
    detoken = decode_jwt_token(token)
    if not detoken:
        flash("Invalid token. Request a new one!")
        return render_template("message.html", messages=get_flashed_messages(),
                               redirect_url = url_for("forgot_password"))
    email = detoken["reset_password"]
    if not email:
        flash("Not correct link!")
        return render_template("message.html", messages=get_flashed_messages(),
                               redirect_url = url_for("forgot_password"))
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("The link is not valid!")
            return render_template("message.html", messages = get_flashed_messages(), redirect_url=url_for("home"))
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash(f"{email}, your password has been reset")
        return render_template("message.html", messages = get_flashed_messages(), redirect_url=url_for("home"))
    return render_template("reset.html", form=form)

def generate_jwt_token(user):
    """generate jwt token for user"""
    return jwt.encode(
        {
            'reset_password': user.email,
            'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=300)
        },
        key=app.config["SECRET_KEY"]
    )

def decode_jwt_token(token):
    """decode the token"""
    try:
        email = jwt.decode(token, key=app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.exceptions.DecodeError as error:
        return None
    return email
