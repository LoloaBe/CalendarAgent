import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

class CalendarAgent:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.SCOPES)
            creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('calendar', 'v3', credentials=creds)

    def get_this_week_appointments(self):
        today = datetime.datetime.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=7)
        
        time_min = start_of_week.isoformat() + 'Z'
        time_max = end_of_week.isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId='primary', 
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        appointments = []
        for event in events_result.get('items', []):
            start = event['start'].get('dateTime', event['start'].get('date'))
            appointments.append({
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'description': event.get('description', 'No description')
            })
        
        return appointments

    def format_appointments(self, appointments):
        if not appointments:
            return "You have no appointments this week."
        
        response = "Here are your appointments this week:\n"
        for appointment in appointments:
            response += f"- {appointment['summary']} on {appointment['start']}\n"
        return response