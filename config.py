# config.py - Configuration SmmKingdomTask SÉCURISÉE
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration Telegram - CHAQUE UTILISATEUR DOIT METTRE SES PROPRES CREDENTIALS
TELEGRAM_CONFIG = {
    "api_id": os.getenv("TELEGRAM_API_ID", ""),  # ← À configurer par l'utilisateur
    "api_hash": os.getenv("TELEGRAM_API_HASH", ""),  # ← À configurer par l'utilisateur
    "session_name": "smm_session",
    "bot_username": "SmmKingdomTasksBot"
}

# Chemins des fichiers
PATHS = {
    "accounts": "/sdcard/SmmKingdomTask/insta-acc.txt",
    "trash": "/sdcard/SmmKingdomTask/corbeille.txt", 
    "logs": "/sdcard/SmmKingdomTask/logs.txt",
    "sessions": "sessions",
    "env_file": ".env"
}

# Couleurs pour l'interface
COLORS = {
    'vi': '\033[1;35m',
    'R': '\033[1;91m', 
    'V': '\033[1;92m',
    'black': '\033[1;30m',
    'J': '\033[1;33m',
    'C': '\033[1;96m',
    'B': '\033[1;97m',
    'Bl': '\033[1;34m',
    'o': '\x1b[38;5;214m',
    'S': '\033[0m'
}

# URLs de contrôle
CONTROL_URLS = {
    "license": "https://raw.githubusercontent.com/Juana-archer/SmmKingdomControl/main/license.json",
    "commands": "https://raw.githubusercontent.com/Juana-archer/SmmKingdomControl/main/commands.json", 
    "version": "https://raw.githubusercontent.com/Juana-archer/SmmKingdomControl/main/version.txt"
}

def setup_telegram_credentials():
    """Guide l'utilisateur pour configurer ses credentials Telegram"""
    env_file = PATHS["env_file"]
    
    if not os.path.exists(env_file):
        print(f"\n{COLORS['J']}🔐 CONFIGURATION TÉLÉGRAM REQUISE{COLORS['S']}")
        print(f"{COLORS['B']}📱 Chaque utilisateur doit obtenir ses propres API credentials{COLORS['S']}")
        print(f"\n{COLORS['C']}📋 PROCÉDURE :{COLORS['S']}")
        print("1. Allez sur https://my.telegram.org/auth")
        print("2. Connectez-vous avec votre compte Telegram")
        print("3. Allez dans 'API Development Tools'")
        print("4. Créez une nouvelle application")
        print("5. Copiez l'API ID et l'API Hash")
        
        api_id = input(f"\n{COLORS['V']}🔢 Entrez votre API ID: {COLORS['S']}")
        api_hash = input(f"{COLORS['V']}🔑 Entrez votre API Hash: {COLORS['S']}")
        
        # Sauvegarde dans .env
        with open(env_file, 'w') as f:
            f.write(f"TELEGRAM_API_ID={api_id}\n")
            f.write(f"TELEGRAM_API_HASH={api_hash}\n")
        
        print(f"{COLORS['V']}✅ Credentials sauvegardés dans {env_file}{COLORS['S']}")
        return True
    else:
        # Vérifie que les credentials sont présents
        with open(env_file, 'r') as f:
            content = f.read()
            if "TELEGRAM_API_ID" not in content or "TELEGRAM_API_HASH" not in content:
                print(f"{COLORS['R']}❌ Fichier .env incomplet{COLORS['S']}")
                os.remove(env_file)
                return setup_telegram_credentials()
        return True

def get_telegram_credentials():
    """Récupère les credentials Telegram"""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print(f"{COLORS['R']}❌ Credentials Telegram manquants{COLORS['S']}")
        setup_telegram_credentials()
        # Recharger les variables
        load_dotenv()
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
    
    return api_id, api_hash

# Initialisation
if __name__ == "__main__":
    setup_telegram_credentials()
