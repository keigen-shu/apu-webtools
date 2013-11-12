# APU Time-table fetcher version 4.2013_02
# written by moogtrian

# That is all the configuration needed. The script will take it from here.
import datetime, re

from apuws import db
from apuws.util import get_first_weekday, get_last_weekday
from flask import url_for

def get_timetable_intake_list():
    intakes = db.session.query(db.Intake.code).all()
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
            if (re.match(regexes[i], intake.code[:5])):
                intake_lists[i].append(intake.code)
                break

    return {
        'groups': groups,
        'intake_lists': intake_lists
    }


def get_timetable_by_intake(intake, week_offset=0):
    entries = db.session.query(db.Entry)\
            .filter(db.Entry.intake_code == intake)\
            .filter(db.Entry.day >= get_first_weekday(week_offset=week_offset))\
            .filter(db.Entry.day <= get_last_weekday(week_offset=week_offset))\
            .all()

    last_date = datetime.date(1957,1,1)
    table = str()

    for entry in entries:
        # filter entries
        if (last_date != entry.day):
            table += '<tr class="section"><td colspan="4">'
            table += entry.day.strftime('%a, %d %B %Y')
            table += '</td></tr>'
            last_date = entry.day

        table += '<tr>'
        table += '<td>' + db.unpack_timeslot(entry.time_slot) + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('room_timetable_now', room=entry.location.room), entry.location.room)
        table += '<td>' + entry.module.code + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('lecturer_timetable', lecturer=entry.lecturer.name, week=0), entry.lecturer.name)
        table += '</tr>'

    return {
        'intake': intake,
        'table': table
    }

def get_lecturer_list():
    lecturers = db.session.query(db.Lecturer.name).all()
    lecturers = sorted(zip(*lecturers)[0])

    groups = [
        '[A-L]',
        '[L-Z]'
    ]
    regexes = [
        r'([ABCDEFGHIJKL])',
        r'.+'
    ]

    lecturer_lists = []

    for i in range(len(groups)):
        lecturer_lists.append([])

    for lecturer in lecturers:
        for i in range(len(groups)):
            if (re.match(regexes[i], lecturer[:2])):
                lecturer_lists[i].append(lecturer)
                break

    return {
        'groups': groups,
        'lecturer_lists': lecturer_lists
    }

def get_timetable_by_lecturer(lecturer, week_offset=0):
    entries = db.session.query(db.Entry)\
            .filter(db.Entry.day >= get_first_weekday(week_offset=week_offset))\
            .filter(db.Entry.day <= get_last_weekday(week_offset=week_offset))\
            .filter(db.Lecturer.id == db.Entry.lecturer_id)\
            .filter(db.Lecturer.name == lecturer)\
            .order_by(db.Entry.day)\
            .order_by(db.Entry.time_slot)\
            .all()

    last_date = datetime.date(1957,1,1)
    table = str()

    for entry in entries:
        # filter entries
        if (last_date != entry.day):
            table += '<tr class="section"><td colspan="4">'
            table += entry.day.strftime('%a, %d %B %Y')
            table += '</td></tr>'
            last_date = entry.day

        table += '<tr>'
        table += '<td>' + db.unpack_timeslot(entry.time_slot) + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('room_timetable_now', room=entry.location.room), entry.location.room)
        table += '<td>' + entry.module.code + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('intake_timetable_now', intake=entry.intake.code), entry.intake.code)
        table += '</tr>'

    return {
        'lecturer': lecturer,
        'table': table
    }


def get_room_list():
    rooms = db.session.query(db.Location.room).all()
    rooms = sorted(zip(*rooms)[0])

    groups = [
        '[TPM]',
        '[ENT3]',
        '[]'
    ]
    regexes = [
        r'(TPM)',
        r'(ENT3)',
        r'.+'
    ]

    room_lists = []

    for i in range(len(groups)):
        room_lists.append([])

    for room in rooms:
        for i in range(len(groups)):
            if (re.match(regexes[i], room[:5])):
                room_lists[i].append(room)
                break

    return {
        'groups': groups,
        'room_lists': room_lists
    }

def get_timetable_by_room(room, week_offset=0):
    entries = db.session.query(db.Entry)\
            .filter(db.Entry.day >= get_first_weekday(week_offset=week_offset))\
            .filter(db.Entry.day <= get_last_weekday(week_offset=week_offset))\
            .filter(db.Location.id == db.Entry.location_id)\
            .filter(db.Location.room == room)\
            .order_by(db.Entry.day)\
            .order_by(db.Entry.time_slot)\
            .all()

    last_date = datetime.date(1957,1,1)
    table = str()

    for entry in entries:
        # filter entries
        if (last_date != entry.day):
            table += '<tr class="section"><td colspan="4">'
            table += entry.day.strftime('%a, %d %B %Y')
            table += '</td></tr>'
            last_date = entry.day

        table += '<tr>'
        table += '<td>' + db.unpack_timeslot(entry.time_slot) + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('intake_timetable_now', intake=entry.intake.code), entry.intake.code)
        table += '<td>' + entry.module.code + '</td>'
        table += '<td><a href="{:}">{:}</a></td>'.format(url_for('lecturer_timetable', lecturer=entry.lecturer.name, week=0), entry.lecturer.name)
        table += '</tr>'

    return {
        'room': room,
        'table': table
    }










