# vim: et:ts=4:sw=4
# APU WebSpace Utilities - v2013.08
# (C) 2013 Keigen Shu

from socket import timeout
import datetime
import re
import urllib

from apu_webtools import db


def dump_intakes():
    # request and obtain intake list
    try:
        response = urllib.urlopen(
            'http://webspace.apiit.edu.my/intake-timetable/')
    except timeout:
        exit('Error: URL request timeout')

    page = response.read()

    s = page.find('<script language="javascript" type="text/javascript">')
    e = page.find('//', s)

    if s == -1 or e == -1:
        exit("Error: could not find page pattern.")

    s = page[s:e].find('data')

    section = page[s:e]

    # extract and print data
    matches = re.findall(r"'([A-Z0-9\{\}]+)'", section)

    if len(matches) == 0:
        exit('Error: intake list is empty')

    return matches



def dump_timetable(intake, week_offset=0):
    # find out the Monday date of the week we want
    week = datetime.date.today()
    week = week + datetime.timedelta(days=-week.weekday(), weeks=week_offset)

    # request timetable
    url = 'http://webspace.apiit.edu.my/intake-timetable/intake-result.php'
    data = urllib.urlencode({
        'week': week.isoformat() + '.xml',
        'selectIntakeAll': intake
    })

    try:
        response = urllib.urlopen(url, data)
    except timeout:
        return 'Error: URL request timeout'

    page = response.read()

    # cut out the time table from the whole page
    s = 100 + page.find(
        '<tr>'
        + '<th>Date</th><th>Time</th><th>Classroom</th>'
        + '<th>Location</th><th>Subject / Module</th><th>Lecturer</th>'
        + '</tr>'
    )   # increment to skip past first <tr>

    e = page.find('<p class="modified-date" >', s)

    if s == -1 or e == -1:
        return 'Error: could not find page pattern'


    section = page[s:e]

    # extract and print data
    matches = re.findall(
        r'(<tr> (?:<td>[^\<\>]+</td> ){6}?</tr>)',
        section
    )
    modified = re.findall(
        r'Last modified: ([^\<\>]+)</p>',
        page[e:e+128]
    )

    if len(modified) == 0:
        modified = None
    else:
        modified = datetime.datetime.strptime(
                modified[0].strip(),
                "%a %d %B %Y %H:%M:%S"
        )

    if len(matches) == 0:
        return intake + ' has no classes on this week'

    entries = []

    for entry in matches:
        fields = re.findall(r'(?:<td> ([^\<\>]+) </td> )', entry)
        entries.append(fields)

    return [ entries, modified ]


def dump_timetables():
    # populate intake list before dumping
    print 'Dropping database...'
    db.session.query(db.Intake).delete()
    db.session.query(db.Module).delete()
    db.session.query(db.Lecturer).delete()
    db.session.query(db.Location).delete()
    db.session.flush()

    print 'Dumping intake list...'
    intakes = dump_intakes()
    modules = set()
    lecturers = set()
    locations = set()
    timetables = dict()

    print 'Dumping timetables...'
    for intake in intakes:
        print '>>> ' + intake + '...'
        dump = dump_timetable(intake)
        if isinstance(dump, basestring):
            print '    ' + dump
        else:
            itk = db.Intake(code=intake, last_update=dump[1])
            db.session.add(itk)

            timetables[intake] = dump[0]

            for col in dump[0]:
                modules.add(col[4])
                lecturers.add(col[5])
                locations.add(col[3] + ' : ' + col[2])

    for module in modules:
        mod = db.Module(code=module, name=module)
        db.session.add(mod)

    for lecturer in lecturers:
        lec = db.Lecturer(name=lecturer)
        db.session.add(lec)

    for location in locations:
        loc = db.Location(room=location)
        db.session.add(loc)

    print 'Populating metadata...'
    db.session.commit()

    print 'Populating entries...'
    for intake, table in timetables.iteritems():
        for entry in table:
            tsd = datetime.datetime.strptime(entry[0], '%a, %d-%b-%Y')
            tst = db.pack_timeslot(entry[1])

            itk = db.session.query(db.Intake)                   \
                    .filter_by(code=intake)                     \
                    .first()

            mod = db.session.query(db.Module)                   \
                    .filter_by(code=entry[4])                   \
                    .first()

            lec = db.session.query(db.Lecturer)                 \
                    .filter_by(name=entry[5])                   \
                    .first()

            loc = db.session.query(db.Location)                 \
                    .filter_by(room=entry[3] + ' : ' + entry[2])\
                    .first()

            new_entry = db.Entry(
                day = tsd,
                time_slot = tst,
                intake_id = itk.id,
                module_id = mod.id,
                lecturer_id = lec.id,
                location_id = loc.id
            )
            db.session.add(new_entry)

    db.session.commit()

    return
