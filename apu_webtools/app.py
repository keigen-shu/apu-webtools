from __future__ import absolute_import, unicode_literals
from flask import Flask, render_template
from apu_webtools.flask_gzip import Gzip
from apu_webtools.timetable import get_timetable, get_timetable_intake_list
from apu_webtools import db

app = Flask(__name__)
zip = Gzip(app, 9)


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


@app.route("/")
def root():
    return render_template('index.html')


@app.route("/timetable")
@app.route("/timetable/")
def timetable_list():
    result = get_timetable_intake_list()
    return render_template(
        'timetable_intakes.html',
        groups=result['groups'],
        intake_lists=result['intake_lists']
    )


@app.route("/timetable/<intake>/<week>")
def timetable(intake, week):
    result = get_timetable(intake, int(week))
    return render_template(
        'timetable.html',
        intake=intake,
        table=result['table'],
        modified=result['modified'],
        week=int(week)
    )


@app.route("/timetable/<intake>")
@app.route("/timetable/<intake>/")
def timetable_now(intake):
    return timetable(intake, 0)
