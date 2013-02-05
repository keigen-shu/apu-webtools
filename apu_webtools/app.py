from __future__ import absolute_import, unicode_literals
from flask import Flask, render_template, request, url_for
from apu_webtools.timetable import get_table

app = Flask(__name__)
"""
@app.route("/")
def root():
    table = get_table('UC2F1301SE')
    return render_template('timetable.html', entries=table['entries'], modified=table['last_modified'])
"""

@app.route("/timetable/<intake>")
def timetable(intake):
    result = get_table(intake)
    return render_template('timetable.html', intake=result['intake'], table=result['table'], modified=result['last_modified'])
