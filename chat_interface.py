# Conversational Interface:

# Runs an interactive loop in chat() method
# Recognizes keywords related to appointments
# Dynamically generates responses about calendar events
# Provides random helpful messages for off-topic inputs
# Allows user to exit conversation

import random

class ChatInterface:
    @staticmethod
    def start_chat(calendar_agent):
        print("Calendar Chat Agent. Type 'exit' to quit.")
        while True:
            user_input = input("You: ").lower()
            
            if user_input in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            if any(phrase in user_input for phrase in ['appointments', 'schedule', 'week', 'calendar']):
                appointments = calendar_agent.get_this_week_appointments()
                print("Agent:", calendar_agent.format_appointments(appointments))
            else:
                responses = [
                    "I can help you with your calendar. Try asking about this week's appointments.",
                    "To get your schedule, ask about your appointments this week.",
                    "I'm your calendar assistant. Ask me about your weekly schedule."
                ]
                print("Agent:", random.choice(responses))