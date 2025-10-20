# config.py
import os
from dotenv import load_dotenv
                                                           load_dotenv()
                                                           # Configuration Telegram
TELEGRAM_CONFIG = {
    "api_id": int(os.getenv('TELEGRAM_API_ID', '21862621')),
    "api_hash": os.getenv('TELEGRAM_API_HASH', '3bb872935b8aa86e2318cedf657a9f0c'),
    "session_name": "smm_session",
    "bot_username": "SmmKingdomTasksBot"
}

# Chemins des fichiers
PATHS = {
    "accounts": "/sdcard/SmmKingdomTask/insta-acc.txt",
    "trash": "/sdcard/SmmKingdomTask/corbeille.txt",
    "logs": "/sdcard/SmmKingdomTask/logs.txt",
    "sessions": "sessions"
}

# Couleurs
COLORS = {
    'vi': '\033[1;35m', 'R': '\033[1;91m', 'V': '\033[1;92m',
    'J': '\033[1;33m', 'C': '\033[1;96m', 'B': '\033[1;97m',
    'o': '\x1b[38;5;214m', 'S': '\033[0m'
}

# Contrôle - URLs importantes
CONTROL_URLS = {
    "license": "https://raw.githubusercontent.com/DahEry/SmmKingdomControl/main/license.json",
    "commands": "https://raw.githubusercontent.com/DahEry/SmmKingdomControl/main/commands.json"
}
