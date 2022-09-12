import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup

from datetime import date, datetime
from dateutil.parser import parse
import pytz
import pendulum
from ics import Calendar, Event
c = Calendar()
dt = pendulum.now()

from config import *
auth=HttpNtlmAuth(user, password)

for i in range(weeks):
    current_week = dt.start_of('week').strftime('%Y-%m-%d')

    url = "https://apps.uclan.ac.uk/TimeTables/SpanWeek/WkMatrix?entId=" + user + "&entType=Student&startDate=" + current_week

    res = requests.get(url, auth=auth)
    print(current_week, "-", res.status_code)

    soup = BeautifulSoup(res.text, features="html.parser")
    
    # remove all empty table cells
    for div in soup.find_all("td", {'class':'TimeTableEmptyCell'}): 
        div.extract()

    # iterate through lessons
    for tr in soup.find_all(class_="otherDay"):
        date = tr.find(class_="date_row_head").text.strip()
        for lesson in tr("td"):
            e = Event()
            i = 0
            description = ""
            for lesson_text in lesson.stripped_strings:
                if(i == 0):
                    e.begin = parse(date + " " + lesson_text.split(" - ")[0] + " +0100", dayfirst=True)
                    e.end = parse(date + " " + lesson_text.split(" - ")[1] + " +0100", dayfirst=True)
                elif(i == 1):
                    e.name = lesson_text
                elif(i == 2):
                    e.location = lesson_text
                else:
                    description += lesson_text + "\n"

                i += 1
                
            e.description = description
            
            print("event -", e.name, e.begin)
            c.events.add(e)

    dt = dt.add(weeks=1)


end = dt.start_of('week').strftime('%Y-%m-%d')
# write .ics file
with open(("Timetable_" + end + '.ics'), 'w') as my_file:
    my_file.writelines(c.serialize_iter())