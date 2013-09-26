# APU Time-table fetcher version 4.2013_02
# written by moogtrian

# That is all the configuration needed. The script will take it from here.
from socket import timeout
import datetime
import re
import urllib


def get_timetable_intake_list():
    # send request and get page
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
        exit('Host intake list is empty')

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

    for intake in sorted(matches):
        for i in range(len(groups)):
            if (re.match(regexes[i], intake[:5])):
                intake_lists[i].append(intake)
                break

    return {
        'groups': groups,
        'intake_lists': intake_lists
    }


def get_timetable(intake, week_inc=0):
    # find out the Monday date of the week we want
    week = datetime.date.today()
    week = week + datetime.timedelta(days=-week.weekday(), weeks=week_inc)

    # send request and get page
    url = 'http://webspace.apiit.edu.my/intake-timetable/intake-result.php' + \
        '?week=' + week.isoformat() + '&selectIntakeAll=' + intake

    try:
        response = urllib.urlopen(url)
    except timeout:
        exit('Error: URL request timeout')

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
        exit("Error: could not find page pattern.")

    section = page[s:e]

    # extract and print data
    matches = re.findall(
        r'(<tr> (?:<td>[^\<\>]+</td> ){6}?</tr>)',
#        r'(<tr> (?:<td> [\s\w:.,\-\/\@\&]+ </td> ){6}?</tr>)',
        section
    )
    modified = re.findall(
        r'Last modified: ([\s\w:]+)</p>',
        page[e:e+128]
    )

    if len(modified) == 0:
        modified = None
    else:
        modified = modified[0].strip()

    last_date = str()
    table = str()

    if len(matches) == 0:
        table = None
    else:
        for entry in matches:
            fields = re.findall(r'(?:<td>([^\<\>]+)</td> )', entry)
            # fields = re.findall(r'(?:<td> ([\s\w:.,\-\/\@\&]+) </td> )', entry)

            # filter entries
            if (last_date != fields[0]):
                table += '<tr class="section"><td colspan="4">'
                table += fields[0]
                table += '</td></tr>'
                last_date = fields[0]

            table += '<tr>'
            table += '<td>' + fields[1] + '</td>'
            table += '<td>' + fields[3] + ' : ' + fields[2] + '</td>'
            table += '<td>' + fields[4] + '</td>'
            table += '<td>' + fields[5] + '</td>'
            table += '</tr>'

    return {
        'intake': intake,
        'week': week.isoformat(),
        'last_modified': modified,
        'table': table
    }




