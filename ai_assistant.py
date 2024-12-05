from dotenv import load_dotenv
import os
import anthropic
from calendar_agent import CalendarAgent
import json
from datetime import datetime

class ConversationalAssistant:
    def __init__(self, timezone='Europe/Berlin'):
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.calendar_agent = CalendarAgent(timezone=timezone)
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def detect_calendar_intent(self, user_input: str) -> dict:
        """Determine if the user's input is calendar-related and what type of operation.

        Args:
            user_input (str): The user's message to analyze

        Returns:
            dict: A JSON structure containing:
                - is_calendar_related (bool): Whether the input is calendar-related
                - operation (str): Type of operation ('read_schedule', 'create_event', or None)
                - time_reference (dict): For reading schedule, contains type and value of time reference
                - event_details (dict): For creating events, contains event information
        """
        system_prompt = """Analyze if the user's message is related to calendar operations. Return JSON response:
        {
            "is_calendar_related": boolean,
            "operation": null | "read_schedule" | "create_event",
            "time_reference": {              # Only if reading schedule
                "type": "day|week|month",
                "value": "today|tomorrow|this_week|next_week|specific_date",
                "date": "YYYY-MM-DD"        # Only for specific dates
            },
            "event_details": {               # Only if creating event
                "title": string,
                "date": "YYYY-MM-DD",        # Current date if not specified
                "date_type": "relative|specific",  # Added to handle relative dates
                "relative_day": "today|tomorrow",  # Only if date_type is relative
                "time": "HH:MM",
                "duration": integer_minutes,
                "description": string
            }
        }

        For relative dates like "tomorrow", set date_type to "relative" and include the relative_day field.
        Always use 24-hour format for time (HH:MM).
        Ensure all dates are in ISO format (YYYY-MM-DD).
        """

        intent_response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}]
        )

        try:
            intent = json.loads(intent_response.content[0].text)
            return intent
        except json.JSONDecodeError:
            return {"is_calendar_related": False, "operation": None}

    def process_query(self, user_input):
        try:
            intent = self.detect_calendar_intent(user_input)
            
            if not intent['is_calendar_related']:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=300,
                    system="You are Claude, an AI Calendar Assistant. While you can engage in general conversation, make sure to remind users that your primary purpose is to help with calendar management when appropriate.",
                    messages=[{"role": "user", "content": user_input}]
                )
                return response.content[0].text

            calendar_context = None
            if intent['operation'] == 'read_schedule':
                start_time, end_time = self.calendar_agent.get_date_range(intent['time_reference'])
                appointments = self.calendar_agent.get_events_for_timerange(start_time, end_time)
                calendar_context = self.calendar_agent.format_appointments(appointments, intent['time_reference'])
            
            elif intent['operation'] == 'create_event':
                event_result = self.calendar_agent.create_event(intent['event_details'])
                calendar_context = f"Event created successfully! You can view it here: {event_result['link']}"

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                system="You are Claude, an AI Calendar Assistant. Respond conversationally while incorporating calendar information when provided.",
                messages=[{
                    "role": "user",
                    "content": f"Calendar context: {calendar_context}\n\nUser message: {user_input}"
                }]
            )
            
            return response.content[0].text

        except Exception as e:
            return f"I encountered an issue while processing that request. Could you please try again or rephrase?"

    def start_chat(self):
        print("\nHello! I'm Claude, your AI Calendar Assistant. I can help you manage your calendar and schedule while also engaging in general conversation.")
        print("\nI can help you with tasks like:")
        print("- Checking your schedule ('What meetings do I have today?')")
        print("- Creating new events ('Schedule a meeting tomorrow at 2pm')")
        print("- Viewing upcoming appointments ('Show me next week's schedule')")
        print("\nFeel free to chat with me about any topic, and whenever you need calendar assistance, just ask!")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye! Let me know if you need help with your calendar again.")
                    break
                if not user_input:
                    continue
                response = self.process_query(user_input)
                print("Claude:", response)
            except Exception as e:
                print("I apologize, but I ran into an issue. Please try again.")