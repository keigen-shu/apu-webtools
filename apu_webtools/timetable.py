# APU Time-table fetcher version 4.2013_02
# written by moogtrian

# That is all the configuration needed. The script will take it from here.
from socket import timeout
from sys import argv
import datetime
import re
import urllib

def get_table(intake, week_inc=0, filters=None):
    # find out the Monday date of the week we want
    week = datetime.date.today()
    week = week + datetime.timedelta(days=-week.weekday(), weeks=week_inc)

    # send request and get page
    url = 'http://webspace.apiit.edu.my/intake-timetable/intake-result.php'
    data = urllib.urlencode({
        'week': week.isoformat() + '.xml',
        'selectIntakeAll': intake 
        })

    try:
        response = urllib.urlopen(url, data)
    except timeout:
        exit('Error: URL request timeout')

    page = response.read()

    # cut out the time table from the whole page
    s = page.find('<tr><th>Date</th><th>Time</th><th>Classroom</th><th>Location</th><th>Subject / Module</th><th>Lecturer</th></tr>', 1500) + 120
    e = page.find('<p class="modified-date" >', s)

    if s == -1 or e == -1:
        exit("Error: could not find page pattern.")

    section = page[s:e]

    # extract and print data
    matches = re.findall(r'(<tr> (?:<td> [\s\w:.,\-\/]+ </td> ){6}?</tr>)', section)
    modified = re.findall(r'Last modified: ([\s\w:]+)</p>', page[e:e+128])

    if len(matches) == 0:
        print("there are no classes")

    last_date = str()
    
    table = str()
    for entry in matches:
        fields = re.findall(r'(?:<td> ([\s\w:.,\-\/]+) </td> )', entry)

        # filter entries
        if (last_date != fields[0]):
            table += '<tr class="section"><td colspan="4">' + fields[0] + '</td></tr>'
            last_date = fields[0]

        table += '<tr><td>' + fields[1] + '</td><td>' + fields[3] + ' : ' + fields[2] + '</td><td>' + fields[4] + '</td><td>' + fields[5] +'</td></tr>'
        
    return {'intake': intake,
            'week': week.isoformat(),
            'last_modified': modified[0].strip(),
            'table': table
            }

