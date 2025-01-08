import requests
import google.generativeai as genai
import time
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from datetime import datetime

scheduled_tasks = {}
# Constants
BOT_TOKEN = "Enter bot token"
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
GENAI_API_KEY = "Enter Demini api key"

# Task Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Initialize Generative AI (Gemini)
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to fetch the latest messages
def get_updates(offset=None):
    try:
        params = {"offset": offset, "timeout": 10}
        response = requests.get(f"{TELEGRAM_API_BASE}/getUpdates", params=params)
        return response.json()
    except Exception as e:
        print("Error fetching updates:", e)
        return None

# Function to send a message to Telegram
def send_message(chat_id, text, reply_to_message_id=None):
    try:
        params = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        response = requests.post(f"{TELEGRAM_API_BASE}/sendMessage", params=params)
        print("Telegram Response:", response.json())
    except Exception as e:
        print("Error sending message:", e)

# Function to handle incoming messages
def handle_message(chat_id, text, message_id):
    if text.startswith("/"):
        # Handle commands
        process_command(chat_id, text.split(" ", 1)[0], text.split(" ", 1)[1] if " " in text else "",message_id)
    else:
        send_message(chat_id, "I didn't understand that. Use /help to see available commands.", reply_to_message_id=message_id)
        

    # elif(text.startswith("/ /gem")):
    #     # Default: Generate response with Gemini
    #     while True:
    #         if(text.startswith("//stop")):
    #             break
    #         else:
    #             try:
    #                 text=text.split(" ", 1)[1]
    #                 response = model.generate_content(text)
    #                 gemini_text = response.candidates[0].content.parts[0].text.strip()
    #                 send_message(chat_id, gemini_text, reply_to_message_id=message_id)
    #             except Exception as e:
    #                 print("Error generating response:", e)
    #                 send_message(chat_id, "Error processing your request. Please try again.", reply_to_message_id=message_id)

def schedule_task(chat_id, args):
    try:
        # Parse time and task
        parts = args.split(" ", 1)
        time_str = parts[0]
        task = parts[1]
        
        # Validate time format
        datetime.strptime(time_str, "%H:%M")
        
        # Add task to dictionary
        if chat_id not in scheduled_tasks:
            scheduled_tasks[chat_id] = []
        scheduled_tasks[chat_id].append({"time": time_str, "task": task})
        
        send_message(chat_id, f"Task scheduled: {task} at {time_str}")
    except (IndexError, ValueError):
        send_message(chat_id, "Invalid format. Use /schedule <time> <task> (e.g., /schedule 12:30 Send report)")

def set_reminder(chat_id, args):
    try:
        # Parse time and message
        parts = args.split(" ", 1)
        time_str = parts[0]
        message = parts[1]
        
        # Validate time format
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now().time()
        
        # Calculate delay in seconds
        current_datetime = datetime.now()
        reminder_datetime = current_datetime.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)
        if reminder_datetime < current_datetime:
            reminder_datetime = reminder_datetime.replace(day=current_datetime.day + 1)
        delay = (reminder_datetime - current_datetime).total_seconds()
        
        # Schedule reminder
        threading.Timer(delay, send_message, args=(chat_id, f"Reminder: {message}")).start()
        
        send_message(chat_id, f"Reminder set for {time_str}: {message}")
    except (IndexError, ValueError):
        send_message(chat_id, "Invalid format. Use /remind <time> <message> (e.g., /remind 15:00 Take a break)")

def show_tasks(chat_id):
    if chat_id in scheduled_tasks and scheduled_tasks[chat_id]:
        tasks = "\n".join([f"{task['time']} - {task['task']}" for task in scheduled_tasks[chat_id]])
        send_message(chat_id, f"Scheduled tasks:\n{tasks}")
    else:
        send_message(chat_id, "No tasks scheduled.")

def doubtbox(chat_id,text,message_id):
        # Default: Generate response with Gemini
                try:
                    # text=text.split(" ", 1)[1]
                    response = model.generate_content(text)
                    gemini_text = response.candidates[0].content.parts[0].text.strip()
                    send_message(chat_id, gemini_text, reply_to_message_id=message_id)

                except Exception as e:
                    print("Error generating response:", e)
                    send_message(chat_id, "Error processing your request. Please try again.", reply_to_message_id=message_id)

# Function to process a command
def process_command(chat_id, command, args,message_id):
    try:
        if command == "/start":
            send_message(chat_id, "Welcome! I can automate tasks for you. Use /help to see available commands.")
        elif command == "/help":
            help_text = (
                "Available Commands:\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/schedule <time> <task> - Schedule a task (e.g., /schedule 12:30 Send report)\n"
                "/remind <time> <message> - Set a reminder (e.g., /remind 15:00 Take a break)\n"
                "/tasks - Show all scheduled tasks\n"
                "/gem- To activate cheatbox/doubtbox to stop:- //stop"
            )
            send_message(chat_id, help_text)

        # create schedule command
        elif command == "/schedule":
            schedule_task(chat_id, args)

        elif command == "/remind":
            set_reminder(chat_id, args)
        elif command == "/tasks":
            show_tasks(chat_id)
        elif command=="/gem":
            doubtbox(chat_id,args,message_id)
        # Additional commands can be added here
        else:
            send_message(chat_id, "Unknown command. Use /help for a list of commands.")
    except Exception as e:
        print("Error processing command:", e)

if __name__ == "__main__":
    last_update_id = None

    print("Bot is running...")

    while True:
        try:
            updates = get_updates(offset=last_update_id)

            if updates and updates.get("result"):
                for update in updates["result"]:
                    update_id = update["update_id"]
                    message = update.get("message")
                    
                    if message and "text" in message:
                        chat_id = message["chat"]["id"]
                        text = message["text"]
                        message_id = message["message_id"]
                        print(f"Received Message: {text} from Chat ID: {chat_id}")
                        handle_message(chat_id, text, message_id)

                        # Update the last processed update_id
                        last_update_id = update_id + 1

        except Exception as e:
            print("Error in main loop:", e)

        time.sleep(1)
