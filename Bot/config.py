import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("TELEGRAM BOT TOKEN не найден в .env файле!")