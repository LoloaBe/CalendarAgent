from dotenv import load_dotenv
import os
import anthropic
from calendar_agent import CalendarAgent

class AICalendarAssistant:
   def __init__(self):
       load_dotenv()
       self.api_key = os.getenv('ANTHROPIC_API_KEY')
       if not self.api_key:
           raise ValueError("ANTHROPIC_API_KEY not found")
       self.calendar_agent = CalendarAgent()
       self.client = anthropic.Anthropic(api_key=self.api_key)

   def process_query(self, user_input):
       context = self.calendar_agent.format_appointments(
           self.calendar_agent.get_this_week_appointments()
       )
       
       response = self.client.messages.create(
           model="claude-3-haiku-20240307",
           max_tokens=300, 
           system="You are a calendar assistant. For event creation requests, extract and return as JSON: intent (create_event or read_calendar), title, start_date (YYYY-MM-DD), start_time (HH:MM), duration, description. For other requests, return {'intent': 'read_calendar'}",
           messages=[{"role": "user", "content": f"Calendar context: {context}\n\nUser query: {user_input}"}]
       )
       return response.content[0].text

   def start_chat(self):
       print("AI Calendar Assistant. Type 'exit' to quit.")
       while True:
           user_input = input("You: ")
           if user_input.lower() in ['exit', 'quit', 'bye']:
               break
           print("Assistant:", self.process_query(user_input))