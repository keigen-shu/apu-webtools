# APU WebSpace Utilities
# (C) 2013 Keigen Shu

from socket import timeout
import datetime
import re
import urllib

from apuws import db
from sqlalchemy import exists

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

# Get the Monday of the week
def get_first_weekday(week_offset=0, date=datetime.date.today()):
    return date + datetime.timedelta(days=-date.weekday(), weeks=week_offset)

# Get the Saturday of the week
def get_last_weekday(week_offset=0, date=datetime.date.today()):
    return date + datetime.timedelta(days=6-date.weekday(), weeks=week_offset)


def dump_timetable(intake, week_offset=0):
    # request timetable
    url = 'http://webspace.apiit.edu.my/intake-timetable/'\
            +'intake-result.php?week={:}&selectIntakeAll={:}'\
            .format(get_first_weekday(week_offset=week_offset).isoformat(),
                    intake)

    try:
        response = urllib.urlopen(url)
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

    if len(matches) == 0:
        return intake + ' has no classes on this week'

    entries = []

    for entry in matches:
        fields = re.findall(r'(?:<td> ([^\<\>]+) </td> )', entry)
        entries.append(fields)

    return entries


def dump_timetables(week_offset=0):
    print 'Dumping intake list...'
    intakes = dump_intakes()
    modules = set()
    lecturers = set()
    locations = set()
    timetables = dict()


    print 'Dumping timetables...'
    new_intakes = 0

    for intake in intakes:
        print '>>> ' + intake + '...'
        dump = dump_timetable(intake, week_offset)
        if isinstance(dump, basestring):
            print '    ' + dump
        else:
            query = db.session.query(db.Intake).filter(db.Intake.code == intake)
            if query.count() == 0:
                itk = db.Intake(code=intake, last_update=datetime.datetime.now())
                db.session.add(itk)
                new_intakes += 1
            else:
                itk = query.one()
                itk.last_update = datetime.datetime.now()

            timetables[intake] = dump

            for col in dump:
                modules.add(col[4])
                lecturers.add(col[5])
                locations.add(col[3] + ' : ' + col[2])

    db.session.commit()


    print 'Populating metadata...'
    new_modules = 0
    new_lecturers = 0
    new_locations = 0

    for module in modules:
        if db.session.query(
            exists().where(db.Module.code == module)
        ).scalar() == False:
            mod = db.Module(code=module)
            db.session.add(mod)
            new_modules += 1

    for lecturer in lecturers:
        if db.session.query(
            exists().where(db.Lecturer.name == lecturer)
        ).scalar() == False:
            lec = db.Lecturer(name=lecturer)
            db.session.add(lec)
            new_lecturers += 1

    for location in locations:
        if db.session.query(
            exists().where(db.Location.room == location)
        ).scalar() == False:
            loc = db.Location(room=location)
            db.session.add(loc)
            new_locations += 1

    db.session.commit()


    print 'Populating entries...'
    entries = 0
    for intake, table in timetables.iteritems():
        # Delete all entries on this week
        db.session.query(db.Entry)\
                .filter(db.Entry.intake_code == intake)\
                .filter(db.Entry.day >= get_first_weekday(week_offset=week_offset))\
                .filter(db.Entry.day <= get_last_weekday(week_offset=week_offset))\
                .delete()

        db.session.flush()

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
                intake_code = itk.code,
                module_code = mod.code,
                lecturer_id = lec.id,
                location_id = loc.id
            )
            db.session.add(new_entry)

    db.session.commit()

    print '{:} intakes found, {:} are new'.format(len(intakes), new_intakes)

    print '{:} modules found, {:} are new'.format(len(modules), new_modules)
    print '{:} lecturers found, {:} are new'.format(len(lecturers), new_lecturers)
    print '{:} locations found, {:} are new'.format(len(locations), new_locations)

    print '{:} timetables found, containing {:} entries'.format(len(timetables), entries)

    return
