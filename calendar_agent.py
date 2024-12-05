from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta, MO

class CalendarAgent:
    def __init__(self, timezone='Europe/Berlin'):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.events', 
                       'https://www.googleapis.com/auth/calendar.readonly']
        self.timezone = pytz.timezone(timezone)
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds or not creds.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                raise Exception(f"Authentication failed: {e}")
        
        return build('calendar', 'v3', credentials=creds)

    def get_events_for_timerange(self, start_datetime, end_datetime):
        try:
            if start_datetime.tzinfo is None:
                start_datetime = self.timezone.localize(start_datetime)
            if end_datetime.tzinfo is None:
                end_datetime = self.timezone.localize(end_datetime)

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_datetime.isoformat(),
                timeMax=end_datetime.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            formatted_events = []
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'id': event['id'],
                    'status': event.get('status', ''),
                    'location': event.get('location', ''),
                    'link': event.get('htmlLink', '')
                })
            
            return formatted_events

        except Exception as e:
            raise Exception(f"Error fetching events: {e}")

    def get_date_range(self, time_reference):
        now = datetime.now(self.timezone)
        
        if time_reference['type'] == 'day':
            if time_reference['value'] == 'today':
                start_date = now
            elif time_reference['value'] == 'tomorrow':
                start_date = now + timedelta(days=1)
            elif time_reference['value'] == 'specific_date':
                start_date = parser.parse(time_reference['date'])
            else:  # specific weekday
                current_weekday = now.weekday()
                target_weekday = time_reference['weekday']
                days_ahead = target_weekday - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                start_date = now + timedelta(days=days_ahead)
                
            start_datetime = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_datetime = start_datetime + timedelta(days=1)
            
        elif time_reference['type'] == 'week':
            if time_reference['value'] == 'this_week':
                start_datetime = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
            elif time_reference['value'] == 'next_week':
                start_datetime = (now + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
            elif time_reference['value'] == 'specific_week':
                start_datetime = parser.parse(time_reference['date'])
                start_datetime = start_datetime - timedelta(days=start_datetime.weekday())
            
            end_datetime = start_datetime + timedelta(days=7)
            
        elif time_reference['type'] == 'month':
            if time_reference['value'] == 'this_month':
                start_datetime = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_datetime = (start_datetime + relativedelta(months=1))
            elif time_reference['value'] == 'next_month':
                start_datetime = (now + relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_datetime = (start_datetime + relativedelta(months=1))
        
        return start_datetime, end_datetime

    def format_appointments(self, appointments, time_reference):
        if not appointments:
            return f"No appointments found for the specified time period."
        
        if time_reference['type'] == 'day':
            if time_reference['value'] == 'today':
                period_desc = "today"
            elif time_reference['value'] == 'tomorrow':
                period_desc = "tomorrow"
            elif time_reference['value'] == 'specific_date':
                date_obj = parser.parse(time_reference['date'])
                period_desc = date_obj.strftime('%A, %B %d, %Y')
            else:
                period_desc = f"this {time_reference['value']}"
        elif time_reference['type'] == 'week':
            if time_reference['value'] == 'this_week':
                period_desc = "this week"
            elif time_reference['value'] == 'next_week':
                period_desc = "next week"
            else:
                period_desc = f"the week of {time_reference['date']}"
        elif time_reference['type'] == 'month':
            period_desc = f"{time_reference['value']}"

        formatted_output = f"Here are your appointments for {period_desc}:\n\n"
        
        current_date = None
        for apt in appointments:
            start_time = datetime.fromisoformat(apt['start'].replace('Z', '+00:00'))
            local_time = start_time.astimezone(self.timezone)
            
            if time_reference['type'] in ['week', 'month']:
                if current_date != local_time.date():
                    current_date = local_time.date()
                    formatted_output += f"{local_time.strftime('%A, %B %d, %Y')}:\n"
            
            formatted_output += self._format_single_appointment(apt, local_time)
        
        return formatted_output

    def _format_single_appointment(self, appointment, local_time):
        output = f"- {appointment['summary']}\n"
        output += f"  Time: {local_time.strftime('%I:%M %p')}\n"
        
        if appointment['description']:
            output += f"  Description: {appointment['description']}\n"
        if appointment['location']:
            output += f"  Location: {appointment['location']}\n"
        
        output += "\n"
        return output

    def create_event(self, event_details):
        try:
            # Handle relative dates like "tomorrow"
            if event_details.get('date_type') == 'relative':
                if event_details['relative_day'] == 'tomorrow':
                    base_date = datetime.now(self.timezone) + timedelta(days=1)
                    start_date = base_date.strftime('%Y-%m-%d')
                else:
                    start_date = event_details['date']
            else:
                start_date = event_details['date']

            # Parse the datetime with explicit timezone
            start_datetime = parser.parse(f"{start_date} {event_details['time']}")
            if start_datetime.tzinfo is None:
                start_datetime = self.timezone.localize(start_datetime)
            
            # Ensure we're using the correct year
            current_year = datetime.now(self.timezone).year
            if start_datetime.year != current_year:
                start_datetime = start_datetime.replace(year=current_year)
            
            end_datetime = start_datetime + timedelta(minutes=int(event_details['duration']))
            
            event = {
                'summary': event_details['title'],
                'location': event_details.get('location', ''),
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': str(self.timezone)
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': str(self.timezone)
                },
                'reminders': {
                    'useDefault': True
                }
            }
            
            if 'attendees' in event_details:
                event['attendees'] = [{'email': email} for email in event_details['attendees']]
            
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            return {
                'status': 'success',
                'event_id': event_result['id'],
                'link': event_result['htmlLink'],
                'datetime': start_datetime.strftime('%Y-%m-%d %H:%M %Z')  # Added for verification
            }
            
        except Exception as e:
            raise Exception(f"Error creating event: {e}")