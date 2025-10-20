# account_manager.py - VERSION AMÉLIORÉE
import json
import os
import requests
import random
import time
from uuid import uuid4                                     from config import PATHS, COLORS
from control_system import ControlSystem

class AccountManager:
    def __init__(self):
        self.accounts_file = PATHS["accounts"]
        self.trash_file = PATHS["trash"]                           self.control = ControlSystem()
        self._ensure_directories()                         
    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        os.makedirs("/sdcard/SmmKingdomTask", exist_ok=True)

    def generate_user_agent(self):
        """Génère un User-Agent réaliste"""
        android_versions = ["10", "11", "12", "13"]
        devices = [
            "SM-G973F", "SM-G975F", "SM-N986B",
            "Mi 9T", "Redmi Note 8", "OnePlus 8"
        ]

        android = random.choice(android_versions)
        device = random.choice(devices)

        return f"Instagram 275.0.0.27.98 Android ({android}/10; 640dpi; 1440x2890; samsung; {device}; {device}; en_US; 454212394)"

    def connect_instagram_account(self, username, password):
        """Connecte un compte Instagram avec meilleure gestion d'erreurs"""
        try:
            print(f"{COLORS['C']}[🔄] Tentative de connexion pour {username}...{COLORS['S']}")

            # Génère un UUID unique
            uid = str(uuid4())

            # Headers améliorés
            headers = {
                'User-Agent': self.generate_user_agent(),
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'X-IG-Capabilities': '3brTvw==',
                'X-IG-Connection-Type': 'WIFI',
                'X-IG-App-ID': '567067343352427',
                'Connection': 'close'
            }

            # Données de connexion
            data = {
                'jazoest': '22265',
                'phone_id': uid,
                'enc_password': f'#PWD_INSTAGRAM:0:0:{password}',
                'username': username,
                'adid': '',
                'guid': uid,
                'device_id': uid,
                'google_tokens': '[]',
                'login_attempt_count': '0'
            }

            # Session avec timeout
            session = requests.Session()
            session.headers.update(headers)

            # Délai aléatoire pour éviter la détection
            time.sleep(random.uniform(2, 5))

            # Tentative de connexion
            response = session.post(
                "https://www.instagram.com/api/v1/accounts/login/",
                data=data,
                timeout=30,
                allow_redirects=True
            )

            print(f"{COLORS['J']}[📡] Code HTTP: {response.status_code}{COLORS['S']}")

            # Vérification de la réponse
            if response.status_code == 200:
                response_data = response.json()

                if response_data.get('status') == 'ok' or 'logged_in_user' in str(response_data):
                    # Récupère les cookies
                    cookies_dict = session.cookies.get_dict()

                    if 'sessionid' in cookies_dict:
                        cookies = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
                        self._save_account(username, cookies)
                        print(f"{COLORS['V']}[✅] SUCCÈS! Compte {username} connecté{COLORS['S']}")
                        return True
                    else:
                        print(f"{COLORS['R']}[❌] Aucun cookie de session reçu{COLORS['S']}")
                        return False
                else:
                    error_message = response_data.get('message', 'Erreur inconnue')
                    print(f"{COLORS['R']}[❌] Erreur Instagram: {error_message}{COLORS['S']}")
                    return False
            else:
                print(f"{COLORS['R']}[❌] Erreur HTTP: {response.status_code}{COLORS['S']}")
                return False

        except requests.exceptions.Timeout:
            print(f"{COLORS['R']}[⏰] Timeout - Vérifiez votre connexion Internet{COLORS['S']}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"{COLORS['R']}[🌐] Erreur de connexion - Pas d'Internet{COLORS['S']}")
            return False
        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur inattendue: {str(e)}{COLORS['S']}")
            return False

    def _save_account(self, username, cookies):
        """Sauvegarde un compte avec vérification des limites"""
        accounts = self.get_all_accounts()
        limits = self.control.get_user_limits()

        if len(accounts) >= limits["max_accounts"]:
            print(f"{COLORS['R']}[⚠️] Limite de {limits['max_accounts']} comptes atteinte{COLORS['S']}")
            return

        with open(self.accounts_file, 'a') as f:
            f.write(f"{username}|{cookies}\n")

        # Rapport de succès
        self.control.send_usage_report("account_connected", {
            "username": username,
            "success": True
        })

    def get_all_accounts(self):
        """Récupère tous les comptes"""
        try:
            with open(self.accounts_file, 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            return []

    def display_accounts(self):
        """Affiche les comptes"""
        accounts = self.get_all_accounts()
        limits = self.control.get_user_limits()

        if not accounts:
            print(f"{COLORS['J']}[⚠️] Aucun compte enregistré{COLORS['S']}")
            return False

        print(f"{COLORS['C']}[📂] Comptes ({len(accounts)}/{limits['max_accounts']}):{COLORS['S']}")
        for i, account in enumerate(accounts, 1):
            username = account.split('|')[0]
            print(f"  {COLORS['o']}[{COLORS['V']}{i}{COLORS['o']}] {username}{COLORS['S']}")
        return True

    def delete_account(self, index):
        """Supprime un compte"""
        accounts = self.get_all_accounts()
        if 0 <= index < len(accounts):
            deleted = accounts.pop(index)

            # Sauvegarde corbeille
            with open(self.trash_file, 'a') as f:
                f.write(f"{deleted}\n")

            # Réécrit le fichier
            with open(self.accounts_file, 'w') as f:
                for acc in accounts:
                    f.write(f"{acc}\n")

            username = deleted.split('|')[0]
            print(f"{COLORS['V']}[🗑️] {username} supprimé{COLORS['S']}")
            return True
        return False
