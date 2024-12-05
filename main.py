from ai_assistant import ConversationalAssistant

def main():
    try:
        assistant = ConversationalAssistant(timezone='Europe/Berlin')
        assistant.start_chat()
    except Exception as e:
        print(f"Error initializing the assistant: {e}")
        print("Please make sure you have:")
        print("1. Set up your ANTHROPIC_API_KEY in the .env file")
        print("2. Have the Google Calendar credentials.json file in the project directory")
        print("3. Installed all required dependencies")

if __name__ == "__main__":
    main()