# AI Calendar Assistant

An AI-powered calendar assistant that uses Claude from Anthropic to interact with Google Calendar through natural language. The assistant can help manage your calendar by understanding your requests conversationally and performing calendar operations.

## Features

- Natural language understanding for calendar operations
- View calendar schedule (today, tomorrow, specific dates)
- Create new calendar events
- Integration with Google Calendar API
- Timezone support
- Conversational interface

## Prerequisites

Before running the assistant, you need:

1. An Anthropic API key for Claude
2. Google Calendar API credentials
3. Python 3.7 or higher

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd calendar-assistant
```

2. Install required dependencies:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic python-dotenv pytz python-dateutil
```

3. Set up your credentials:
   - Create a `.env` file in the project root and add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Place your Google Calendar API credentials file (`credentials.json`) in the project root

## Project Structure

```
calendar-assistant/
├── main.py              # Entry point
├── ai_assistant.py         # AI Assistant implementation
├── calendar_agent.py    # Google Calendar operations
├── .env                 # Environment variables
├── credentials.json     # Google Calendar credentials
└── README.md
```

## Usage

Run the assistant:
```bash
python main.py
```

Example interactions:
```
You: What meetings do I have today?
Assistant: Let me check your calendar...

You: Schedule a meeting tomorrow at 2pm
Assistant: I'll help you create that event...
```

## Configuration

The assistant uses Europe/Berlin timezone by default. You can change this by modifying the timezone parameter when initializing the ConversationalAssistant:

```python
assistant = ConversationalAssistant(timezone='Your/Timezone')
```

## Dependencies

- `google-auth-oauthlib`: Google authentication
- `google-api-python-client`: Google Calendar API client
- `anthropic`: Claude API client
- `python-dotenv`: Environment variable management
- `pytz`: Timezone handling
- `python-dateutil`: Date parsing and manipulation

## Author

Luca Criscuolo

## License

MIT

## Acknowledgments

- Anthropic for the Claude AI model
- Google Calendar API