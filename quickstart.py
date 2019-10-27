from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GCalendar:

    def __init__(self):
        pass

    def insert_event(self, activity):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('./data/token.pickle'):
            with open('./data/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './data/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('./data/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

        # activity = ("IntelligentAgents", "Monday")
        weekday, weekday_, summary = GCalendar.plan_weekday(activity[1], activity[0])

        event = {
          'summary': summary,
          'location': 'Utrecht Science Park',
          'description': 'A chance to hear more about OWL',
          'start': {
            'dateTime': weekday,
            'timeZone': 'Europe/Amsterdam',
          },
          'end': {
            'dateTime': weekday_,
            'timeZone': 'Europe/Amsterdam',
          },
          'recurrence': [
            'RRULE:FREQ=WEEKLY;COUNT=14'
          ],
          'attendees': [
            {'email': 'O.Hundogan@gmail.com'},
            {'email': 'sbrin@example.com'},
          ],
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'email', 'minutes': 24 * 60},
              {'method': 'popup', 'minutes': 10},
            ],
          },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    @staticmethod
    def plan_weekday(activity_weekday, activity_name):
        d = 4
        if activity_weekday == "Monday":
            d += 0
        if activity_weekday == "Tuesday":
            d += 1
        # contiune
        datetime = '2019-11-{}T09:00:00-07:00'.format(d)
        datetime_ = '2019-11-{}T11:00:00-07:00'.format(d)
        summary = activity_name
        return datetime, datetime_, summary
