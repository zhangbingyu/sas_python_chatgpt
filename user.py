from models import Transaction, User
from app import app, db
from flask_login import current_user
from flask import render_template, request

@app.route("/user")
def user():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    transactions = Transaction.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page)
    return render_template("user.html", transactions=transactions)