import flask
from flask import render_template
from calender_system import CalendarSystem


calendar_system = CalendarSystem(num_weeks=8)

app = flask.Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about_fun():
    return  render_template("about.html")

@app.route("/schedule")
def schedule_fun():
    print(calendar_system.calendar)
    return  render_template("schedule.html",availability = calendar_system.calendar)

@app.route("/contact")
def contact_fun():
    return  render_template("contact.html")

@app.route("/programme")
def programme_fun():
    return render_template("programme.html")

@app.route("/statistics")
def statistics_fun():
    return  render_template("statistics.html")

app.run(debug=True)