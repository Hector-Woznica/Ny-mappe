import flask
from flask import render_template

app = flask.Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about_fun():
    return  render_template("about.html")

@app.route("/schedule")
def schedule_fun():
    return  render_template("schedule.html")

@app.route("/contact")
def contact_fun():
    return  render_template("contact.html")

@app.route("/statistics")
def statistics_fun():
    return  render_template("statistics.html")

app.run(debug=True)