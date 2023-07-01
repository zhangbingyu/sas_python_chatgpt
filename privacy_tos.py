from flask import render_template
from app import app

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/tos")
def tos():
    return render_template("tos.html") 