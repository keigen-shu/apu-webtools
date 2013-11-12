from __future__ import absolute_import, unicode_literals
from flask import Flask, redirect, render_template, url_for
from apuws import util, flask_gzip
from apuws.timetable import get_timetable_intake_list, get_timetable_by_intake
from apuws.timetable import get_lecturer_list, get_timetable_by_lecturer
from apuws.timetable import get_room_list, get_timetable_by_room

from apscheduler.scheduler import Scheduler

sched = Scheduler()
sched.start()

def dump_this_week():
    util.dump_timetables(0)

def dump_next_week():
    util.dump_timetables(1)

# Update tables on these hours
sched.add_cron_job(dump_this_week, day_of_week='mon-fri', hour='0,4,8-20')

# Update tables on fri-sun
sched.add_cron_job(dump_next_week, day_of_week='fri-sun', hour='0,6,12,18')


app = Flask(__name__)
zip = flask_gzip.Gzip(app, 9)

@app.route("/")
def root():
    return render_template('index.html')


@app.route("/refresh/")
def refresh_database():
    util.dump_timetables()
    return render_template('index.html')


@app.route("/timetable/intake/")
def intake_list():
    result = get_timetable_intake_list()
    return render_template(
        'timetable_intakes.html',
        groups=result['groups'],
        intake_lists=result['intake_lists']
    )


@app.route("/timetable/intake/<intake>/")
def intake_timetable_now(intake):
    return redirect(url_for('intake_timetable', intake=intake, week=0))

@app.route("/timetable/intake/<intake>/<week>/")
def intake_timetable(intake, week):
    result = get_timetable_by_intake(intake, int(week))
    return render_template(
        'timetable.html',
        intake=result['intake'],
        lecturer=None,
        room=None,
        table=result['table'],
        week=int(week)
    )

@app.route("/timetable/lecturer/")
def lecturer_list():
    result = get_lecturer_list()
    return render_template('timetable_lecturers.html',
                           groups=result['groups'],
                           lecturer_lists=result['lecturer_lists'])

@app.route("/timetable/lecturer/<path:lecturer>/<week>/")
def lecturer_timetable(lecturer, week):
    result = get_timetable_by_lecturer(lecturer, int(week))
    return render_template(
        'timetable.html',
        intake=None,
        lecturer=result['lecturer'],
        room=None,
        table=result['table'],
        week=int(week)
    )

@app.route("/timetable/room/")
def room_list():
    result = get_room_list()
    return render_template('timetable_rooms.html',
                           groups=result['groups'],
                           room_lists=result['room_lists'])

@app.route("/timetable/room/<room>/")
def room_timetable_now(room):
    return redirect(url_for('room_timetable', room=room, week=0))

@app.route("/timetable/room/<room>/<week>/")
def room_timetable(room, week):
    result = get_timetable_by_room(room, int(week))
    return render_template(
        'timetable.html',
        intake=None,
        lecturer=None,
        room=result['room'],
        table=result['table'],
        week=int(week)
    )
