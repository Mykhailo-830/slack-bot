import os
from dotenv import load_dotenv
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables from .env file
load_dotenv()

# Get environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure tokens are loaded
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing environment variables! Check your .env file.")

# Define the allowed channel ID (replace with your actual channel ID)
ALLOWED_CHANNEL_ID = "C08GTEV177S"  # Only allow this Slack channel

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Function to get AI response from OpenAI
def get_openai_response(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a helpful AI assistant that answers like a real human, not a chatbot. "
                "You have a good sense of humor and respond with humor and emojis. "
                "If someone asks an impolite or illegal question, reply with 'Do you want to get kicked out?'. "
                "If they agree, respond with 'I will report to the admin, wait...'"
            )},
            {"role": "user", "content": user_message}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Handle messages and reply in threads (only in allowed channel)
@app.event("message")
def handle_message(event, client):
    print(f"Received event: {event}")  # Debugging output

    channel_id = event["channel"]
    user = event.get("user", "")
    text = event.get("text", "").strip()  # Ensure no empty messages
    bot_id = event.get("bot_id")  # Check if message is from a bot

    # Ignore bot messages
    if bot_id:
        print("Ignoring bot message")
        return

    # Ignore messages that are empty or just whitespace
    if not text:
        print("Ignoring empty message")
        return

    # Process AI response only for actual user messages
    ai_reply = get_openai_response(text)

    # Reply in the same thread
    thread_ts = event.get("thread_ts", event["ts"])
    client.chat_postMessage(
        channel=channel_id,
        text=f"🤖 {ai_reply}",
        thread_ts=thread_ts
    )


# Start the bot
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()




