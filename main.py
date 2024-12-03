from calendar_agent import CalendarAgent
from chat_interface import ChatInterface

def main():
    agent = CalendarAgent()
    ChatInterface.start_chat(agent)

if __name__ == '__main__':
    main()