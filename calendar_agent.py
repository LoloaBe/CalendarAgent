import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

class CalendarAgent:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']  # Full access
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', self.SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('calendar', 'v3', credentials=creds)

    def get_this_week_appointments(self):
        today = datetime.datetime.now()
        week_start = today - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=7)
        
        events = self.service.events().list(
            calendarId='primary', 
            timeMin=week_start.isoformat() + 'Z',
            timeMax=week_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return [{
            'summary': event.get('summary', 'No Title'),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'description': event.get('description', 'No description')
        } for event in events.get('items', [])]

    def format_appointments(self, appointments):
        if not appointments:
            return "You have no appointments this week."
        return "Here are your appointments this week:\n" + "\n".join(
            f"- {apt['summary']} on {apt['start']}" for apt in appointments
        )