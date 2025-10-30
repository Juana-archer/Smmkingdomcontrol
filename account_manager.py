# account_manager.py - GESTION COMPLÈTE DES COMPTES INSTAGRAM
import json
import os
import requests
import time
import re
import random
import asyncio
from config import PATHS, COLORS

class AccountManager:
    def __init__(self):
        self.accounts_file = PATHS["accounts"]
        self.trash_file = PATHS["trash"]
        self.passwords_file = "/sdcard/SmmKingdomTask/account_passwords.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """Crée les dossiers nécessaires"""
        os.makedirs("/sdcard/SmmKingdomTask", exist_ok=True)
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'w') as f:
                f.write("# Fichier des comptes Instagram\n")
        if not os.path.exists(self.passwords_file):
            with open(self.passwords_file, 'w') as f:
                json.dump({}, f)

    def save_account_password(self, username, password):
        """Sauvegarde un mot de passe pour la réparation auto"""
        try:
            with open(self.passwords_file, 'r') as f:
                passwords = json.load(f)
        except:
            passwords = {}

        passwords[username] = password

        with open(self.passwords_file, 'w') as f:
            json.dump(passwords, f, indent=2)

        print(f"{COLORS['V']}[🔐] Mot de passe sauvegardé pour {username}{COLORS['S']}")
        return True

    def get_password(self, username):
        """Récupère un mot de passe pour la réparation"""
        try:
            with open(self.passwords_file, 'r') as f:
                passwords = json.load(f)
                return passwords.get(username)
        except:
            return None

    def get_advanced_headers(self):
        """Headers complets pour contourner les protections"""
        return {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def get_initial_session(self):
        """Établit une session initiale avec Instagram"""
        try:
            session = requests.Session()
            session.headers.update(self.get_advanced_headers())

            print(f"{COLORS['C']}[🌐] Initialisation de la session...{COLORS['S']}")

            # Première requête pour récupérer les cookies initiaux
            response = session.get(
                "https://www.instagram.com/accounts/login/",
                timeout=30,
                allow_redirects=True
            )

            if response.status_code == 200:
                # Extraire le CSRF token
                csrf_match = re.search(r'"csrf_token":"([^"]+)"', response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"{COLORS['V']}[🔑] CSRF Token récupéré{COLORS['S']}")
                else:
                    csrf_token = session.cookies.get('csrftoken', '')
                    print(f"{COLORS['J']}[⚠️] CSRF depuis cookies{COLORS['S']}")

                print(f"{COLORS['C']}[🍪] Cookies initiaux: {len(session.cookies.get_dict())}{COLORS['S']}")
                return session, csrf_token
            else:
                print(f"{COLORS['R']}[❌] Erreur initialisation: {response.status_code}{COLORS['S']}")
                return None, None

        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur session: {e}{COLORS['S']}")
            return None, None

    def connect_instagram_account(self, username, password):
        """Nouvelle méthode avec gestion complète de l'authentification"""
        print(f"{COLORS['C']}=== CONNEXION INSTAGRAM AVANCÉE ==={COLORS['S']}")

        # ÉTAPE 1: Initialiser la session
        session, csrf_token = self.get_initial_session()
        if not session:
            return False

        try:
            # ÉTAPE 2: Préparer les données de connexion
            login_data = {
                'username': username,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': '{}',
                'stopDeletionNonce': ''
            }

            # ÉTAPE 3: Headers pour la connexion
            login_headers = {
                'User-Agent': session.headers['User-Agent'],
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'Referer': 'https://www.instagram.com/accounts/login/',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.instagram.com'
            }

            # Délai aléatoire
            wait_time = random.uniform(2, 4)
            print(f"{COLORS['J']}[⏰] Attente de {wait_time:.1f}s...{COLORS['S']}")
            time.sleep(wait_time)

            # ÉTAPE 4: Tentative de connexion
            print(f"{COLORS['C']}[📡] Envoi de la requête de connexion...{COLORS['S']}")

            response = session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                data=login_data,
                headers=login_headers,
                timeout=30,
                allow_redirects=False
            )

            print(f"{COLORS['J']}[📊] Code HTTP: {response.status_code}{COLORS['S']}")

            if response.status_code == 200:
                try:
                    response_data = response.json()

                    if response_data.get('authenticated') == True:
                        print(f"{COLORS['V']}[✅] Authentification réussie!{COLORS['S']}")

                        home_response = session.get("https://www.instagram.com/", timeout=20, allow_redirects=True)

                        final_cookies = session.cookies.get_dict()
                        print(f"{COLORS['C']}[🍪] Cookies finaux: {len(final_cookies)} cookie(s){COLORS['S']}")

                        if 'sessionid' in final_cookies and 'csrftoken' in final_cookies:
                            print(f"{COLORS['V']}[🎉] Session ID valide récupéré!{COLORS['S']}")
                            self._save_account(username, final_cookies)
                            self.save_account_password(username, password)
                            return True
                        else:
                            print(f"{COLORS['R']}[❌] Cookies session manquants{COLORS['S']}")
                            return False

                    else:
                        error_msg = response_data.get('message', 'Non authentifié')
                        if 'checkpoint' in error_msg.lower():
                            print(f"{COLORS['R']}[🚫] Vérification sécurité requise{COLORS['S']}")
                        elif 'password' in error_msg.lower():
                            print(f"{COLORS['R']}[❌] Mot de passe incorrect{COLORS['S']}")
                        else:
                            print(f"{COLORS['R']}[❌] Erreur: {error_msg}{COLORS['S']}")
                        return False

                except requests.exceptions.JSONDecodeError:
                    print(f"{COLORS['R']}[❌] Réponse non-JSON{COLORS['S']}")
                    return False

            else:
                print(f"{COLORS['R']}[❌] Erreur HTTP: {response.status_code}{COLORS['S']}")
                return False

        except requests.exceptions.Timeout:
            print(f"{COLORS['R']}[⏰] Timeout{COLORS['S']}")
            return False
        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur: {str(e)}{COLORS['S']}")
            return False

    def _save_account(self, username, cookies):
        """Sauvegarde le compte"""
        try:
            account_line = f"{username}|{json.dumps(cookies)}\n"
            with open(self.accounts_file, 'a', encoding='utf-8') as f:
                f.write(account_line)
            print(f"{COLORS['V']}[💾] Compte sauvegardé avec succès!{COLORS['S']}")
        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur sauvegarde: {e}{COLORS['S']}")

    def get_all_accounts(self):
        """Récupère tous les comptes"""
        accounts = []
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            if '|' in line:
                                username, cookies_str = line.split('|', 1)
                                cookies_dict = json.loads(cookies_str)
                                if isinstance(cookies_dict, dict):
                                    accounts.append((username, cookies_str))
                        except:
                            continue
            return accounts
        except FileNotFoundError:
            return []

    def display_accounts(self):
        """Affiche les comptes"""
        accounts = self.get_all_accounts()
        if not accounts:
            print(f"{COLORS['J']}[📭] Aucun compte enregistré{COLORS['S']}")
            return False

        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║          COMPTES INSTAGRAM            ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")

        for i, (username, cookies_str) in enumerate(accounts, 1):
            try:
                cookies = json.loads(cookies_str)
                if 'sessionid' in cookies:
                    status = f"{COLORS['V']}✅ ACTIF{COLORS['S']}"
                else:
                    status = f"{COLORS['R']}❌ INACTIF{COLORS['S']}"

                print(f"{COLORS['B']}║ {COLORS['V']}{i:2d}.{COLORS['S']} {username:<20} {status} {COLORS['B']}║{COLORS['S']}")

            except:
                print(f"{COLORS['B']}║ {COLORS['R']}{i:2d}.{COLORS['S']} {username:<20} ❌ INVALIDE {COLORS['B']}║{COLORS['S']}")

        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print(f"{COLORS['J']}📊 Total: {len(accounts)} compte(s){COLORS['S']}")
        return True

    def delete_account(self, index):
        """Supprime un compte"""
        accounts = self.get_all_accounts()
        if 0 <= index < len(accounts):
            deleted_account = accounts.pop(index)
            username = deleted_account[0]

            try:
                with open(self.trash_file, 'a', encoding='utf-8') as f:
                    f.write(f"{username}|{deleted_account[1]}\n")
            except:
                pass

            try:
                with open(self.accounts_file, 'w', encoding='utf-8') as f:
                    f.write("# Fichier des comptes Instagram\n")
                    for acc in accounts:
                        f.write(f"{acc[0]}|{acc[1]}\n")

                print(f"{COLORS['V']}[🗑️] Compte {username} supprimé{COLORS['S']}")
                return True
            except Exception as e:
                print(f"{COLORS['R']}[💥] Erreur suppression: {e}{COLORS['S']}")
                return False
        else:
            print(f"{COLORS['R']}[❌] Index invalide{COLORS['S']}")
            return False

    def get_random_account(self):
        """Retourne un compte aléatoire"""
        accounts = self.get_all_accounts()
        if accounts:
            return random.choice(accounts)
        return None

    def get_account_by_username(self, username):
        """Retourne un compte spécifique par username"""
        accounts = self.get_all_accounts()
        for acc in accounts:
            if acc[0] == username:
                return acc
        return None

    def validate_account(self, username, cookies_str):
        """Valide qu'un compte a des cookies valides"""
        try:
            cookies = json.loads(cookies_str)
            return 'sessionid' in cookies and 'csrftoken' in cookies
        except:
            return False

    def count_accounts(self):
        """Compte le nombre de comptes"""
        return len(self.get_all_accounts())

# Test direct
if __name__ == "__main__":
    manager = AccountManager()
    print(f"{COLORS['C']}=== TEST DE CONNEXION INSTAGRAM ==={COLORS['S']}")
    username = input(f"{COLORS['B']}[?] Username: {COLORS['S']}")
    password = input(f"{COLORS['B']}[?] Password: {COLORS['S']}")

    success = manager.connect_instagram_account(username, password)

    if success:
        print(f"{COLORS['V']}🎉 COMPTE AJOUTÉ AVEC SUCCÈS!{COLORS['S']}")
    else:
        print(f"{COLORS['R']}💔 ÉCHEC DE LA CONNEXION{COLORS['S']}")
