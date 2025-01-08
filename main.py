import requests
import google.generativeai as genai
import time

# Constants
BOT_TOKEN = "8167051716:AAE242n4ytRAPfj8aV8_KFGqMX2z4PKGgug"
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
GENAI_API_KEY = "AIzaSyDPDeqKsPWVb_gMS7lcRf7FcNivlh0gUVU"

# Initialize Generative AI (Gemini)
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to fetch the latest messages
def get_updates(offset=None):
    """Fetches updates from Telegram."""
    try:
        params = {"offset": offset, "timeout": 10}
        response = requests.get(f"{TELEGRAM_API_BASE}/getUpdates", params=params)
        return response.json()
    except Exception as e:
        print("Error fetching updates:", e)
        return None

# Function to send a message to Telegram
def send_message(chat_id, text):
    """Sends a message to a specific chat ID via Telegram."""
    try:
        params = {"chat_id": chat_id, "text": text}
        response = requests.post(f"{TELEGRAM_API_BASE}/sendMessage", params=params)
        print("Telegram Response:", response.json())
    except Exception as e:
        print("Error sending message:", e)

# Function to send an audio file to Telegram
def send_audio(chat_id, audio_url):
    """Sends an audio file to a specific chat ID via Telegram."""
    try:
        params = {"chat_id": chat_id, "audio": audio_url}
        response = requests.post(f"{TELEGRAM_API_BASE}/sendAudio", params=params)
        print("Telegram Audio Response:", response.json())
    except Exception as e:
        print("Error sending audio:", e)

# Function to send a photo to Telegram
def send_photo(chat_id, photo_url, caption=None):
    """Sends a photo to a specific chat ID via Telegram."""
    try:
        params = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
        response = requests.post(f"{TELEGRAM_API_BASE}/sendPhoto", params=params)
        print("Telegram Photo Response:", response.json())
    except Exception as e:
        print("Error sending photo:", e)

# Function to process a message and generate a Gemini response
def process_message(chat_id, message_text):
    """Processes a user's message and generates an appropriate response."""
    try:
        # Check if the message is a request for specific media
        if message_text.lower().startswith("send audio"):
            audio_url = "https://example.com/sample_audio.mp3"  # Replace with a valid audio file URL
            send_audio(chat_id, audio_url)
            return

        elif message_text.lower().startswith("send photo"):
            photo_url = "https://example.com/sample_photo.jpg"  # Replace with a valid photo file URL
            send_photo(chat_id, photo_url, caption="Here is your photo!")
            return

        else:
            # Generate a response using Gemini for general messages
            response = model.generate_content(message_text)
            gemini_text = response.candidates[0].content.parts[0].text.strip()
            print("Gemini Response:", gemini_text)

            # Send the generated text to Telegram
            send_message(chat_id, gemini_text)

    except Exception as e:
        print("Error generating or sending response:", e)

if __name__ == "__main__":
    last_update_id = None  # To track the last processed update

    print("Bot is running...")

    while True:
        try:
            # Fetch updates from Telegram
            updates = get_updates(offset=last_update_id)

            if updates and updates.get("result"):
                for update in updates["result"]:
                    # Extract update_id and message details
                    update_id = update["update_id"]
                    message = update.get("message")

                    if message and "text" in message:
                        chat_id = message["chat"]["id"]
                        text = message["text"]

                        print(f"Received Message: {text} from Chat ID: {chat_id}")

                        # Process the message and respond
                        process_message(chat_id, text)

                        # Update the last processed update_id
                        last_update_id = update_id + 1

        except Exception as e:
            print("An error occurred in the main loop:", e)

        # Short delay to avoid flooding the API
        time.sleep(1)
