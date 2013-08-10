# vim: et:ts=4:sw=4
# Timetable logic
# (C) 2013 Keigen Shu

# That is all the configuration needed. The script will take it from here.
from socket import timeout
import datetime
import re
import urllib
from apu_webtools import db

def get_timetable_intake_list():
    intakes = db.session.query(db.Intake).order_by(db.Intake.code)

    if not intakes:
        return 'Intake list is empty.'
    else:
        # TODO assign group category in database
        groups = [
            'UCM / UCP',
            'UCDF / UCFF',
            'UC1F',
            'UC2F',
            'UC3F',
            'UC4F / Others'
        ]
        regexes = [
            r'(UCM)|(UC[123]?P)',
            r'(UCD[12]?F)|(UCFF)',
            r'(UC1F)',
            r'(UC2F)',
            r'(UC3F)',
            r'.+'
        ]

        intake_lists = []

        for i in range(len(groups)):
            intake_lists.append([])

        for intake in intakes:
            for i in range(len(groups)):
                if (re.match(regexes[i], intake.code)):
                    intake_lists[i].append(intake.code)
                    break

        return {
            'groups': groups,
            'intake_lists': intake_lists
        }

def get_timetable(intake, week_inc=0):
    table = str()
    # find out the Monday date of the week we want
    week = datetime.date.today()
    week = week + datetime.timedelta(days=-week.weekday(), weeks=week_inc)

    io = db.session.query(db.Intake).filter_by(code=intake).first()
    if not io:
        return {
            'week': week.isoformat(),
            'table': 'Intake does not exist'
        }

    entries = db.session.query(db.Entry).filter_by(intake_id=io.id).order_by(db.Entry.day)
    if not entries:
        return {
            'week': week.isoformat(),
            'table': 'Intake time-table is empty'
        }

    last_date = str()

    for entry in entries:
        # filter entries
        if (last_date != entry.day):
            last_date  = entry.day
            table += '<tr class="section"><td colspan="4">'
            table += last_date.strftime("%a, %d %B %Y")
            table += '</td></tr>'

        table += '<tr>'
        table += '<td>' + db.unpack_timeslot(entry.time_slot) + '</td>'
        table += '<td>' + entry.location.room + '</td>'
        table += '<td>' + entry.module.name + '</td>'
        table += '<td>' + entry.lecturer.name + '</td>'
        table += '</tr>'

    return {
        'week': week.isoformat(),
        'modified': io.last_update,
        'table': table
    }

