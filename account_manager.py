import json
import os
import requests
import time
import re
import random
from datetime import datetime

class AccountManager:
    def __init__(self, accounts_file="instagram_accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = self.load_accounts()
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/115.0 Firefox/115.0',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]

    def load_accounts(self):
        """Charge les comptes depuis le fichier JSON"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                    print(f"✅ {len(accounts_data)} compte(s) chargé(s)")

                    # S'assurer que tous les comptes ont les champs requis
                    for username, data in accounts_data.items():
                        if 'cookies' not in data:
                            data['cookies'] = ''
                        if 'password' not in data:
                            data['password'] = ''
                        if 'status' not in data:
                            data['status'] = 'active'

                    return accounts_data
            except Exception as e:
                print(f"❌ Erreur chargement: {e}")
                return {}
        else:
            print(f"📁 Création nouveau fichier: {self.accounts_file}")
            return {}

    def save_accounts(self):
        """Sauvegarde les comptes"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False

    # ✅ MÉTHODES MANQUANTES AJOUTÉES
    def get_all_accounts(self):
        """Retourne tous les comptes - MÉTHODE MANQUANTE"""
        return self.accounts

    def get_account_count(self):
        """Retourne le nombre de comptes - MÉTHODE MANQUANTE"""
        return len(self.accounts)

    def get_active_accounts(self):
        """Retourne tous les comptes actifs - MÉTHODE MANQUANTE"""
        active_accounts = []
        for username, data in self.accounts.items():
            if data.get('status') != 'inactive':
                active_accounts.append({
                    'username': username,
                    'cookies': data.get('cookies', ''),
                    'session_data': data.get('session_data', ''),
                    'password': data.get('password', '')
                })
        return active_accounts

    def get_random_account(self):
        """Retourne un compte aléatoire actif - MÉTHODE MANQUANTE"""
        active_accounts = self.get_active_accounts()
        if active_accounts:
            return random.choice(active_accounts)
        return None

    def get_account_by_username(self, username):
        """Retourne un compte spécifique - MÉTHODE MANQUANTE"""
        return self.accounts.get(username)

    def check_single_account_status(self, username):
        """Vérifie le statut d'un compte - MÉTHODE MANQUANTE"""
        if username in self.accounts:
            account_data = self.accounts[username]
            cookies = account_data.get('cookies', '')
            status = account_data.get('status', 'unknown')

            if cookies and 'sessionid' in cookies and status == 'active':
                return "active"
            return "no_session"
        return "not_found"

    def add_account(self, username, password, cookies="", session_data=""):
        """Ajoute un compte manuellement - MÉTHODE MANQUANTE"""
        self.accounts[username] = {
            'password': password,
            'cookies': cookies,
            'session_data': session_data,
            'last_used': datetime.now().isoformat(),
            'status': 'active'
        }
        return self.save_accounts()

    def delete_account(self, username):
        """Supprime un compte - MÉTHODE MANQUANTE"""
        if username in self.accounts:
            del self.accounts[username]
            if self.save_accounts():
                print(f"✅ Compte {username} supprimé")
                return True
        print(f"❌ Compte {username} non trouvé")
        return False

    # ✅ MÉTHODES POUR INSTAGRAPi
    def get_account_for_instagrapi(self, username):
        """Retourne les données formatées pour instagrapi"""
        if username not in self.accounts:
            return None

        account_data = self.accounts[username]

        return {
            'username': username,
            'password': account_data.get('password', ''),
            'cookies': account_data.get('cookies', ''),
            'status': account_data.get('status', 'active'),
            'last_used': account_data.get('last_used', '')
        }

    def get_all_usernames(self):
        """Retourne tous les noms d'utilisateurs"""
        return list(self.accounts.keys())

    def update_account_cookies(self, username, cookies_str):
        """Met à jour les cookies d'un compte"""
        if username in self.accounts:
            self.accounts[username]['cookies'] = cookies_str
            self.accounts[username]['last_used'] = datetime.now().isoformat()
            return self.save_accounts()
        return False

    def validate_session(self, username):
        """Valide si une session est encore active"""
        if username not in self.accounts:
            return False

        account_data = self.accounts[username]
        cookies = account_data.get('cookies', '')

        if not cookies or 'sessionid' not in cookies:
            return False

        last_used = account_data.get('last_used', '')
        if last_used:
            try:
                last_date = datetime.fromisoformat(last_used)
                if (datetime.now() - last_date).days > 7:
                    return False
            except:
                pass

        return True

    def get_active_accounts_info(self):
        """Retourne les infos des comptes actifs"""
        active_accounts = []
        for username, data in self.accounts.items():
            if data.get('status') == 'active':
                active_accounts.append({
                    'username': username,
                    'has_password': bool(data.get('password')),
                    'has_cookies': bool(data.get('cookies')),
                    'last_used': data.get('last_used', 'Never')
                })
        return active_accounts

    def mark_account_problem(self, username, reason=""):
        """Marque un compte comme ayant des problèmes"""
        if username in self.accounts:
            self.accounts[username]['status'] = 'problem'
            self.accounts[username]['last_error'] = reason
            self.accounts[username]['error_time'] = datetime.now().isoformat()
            self.save_accounts()
            print(f"🚫 Compte {username} marqué comme problématique: {reason}")

    def reactivate_account(self, username):
        """Réactive un compte précédemment problématique"""
        if username in self.accounts:
            self.accounts[username]['status'] = 'active'
            if 'last_error' in self.accounts[username]:
                del self.accounts[username]['last_error']
            self.save_accounts()
            print(f"✅ Compte {username} réactivé")

    def connect_with_instagrapi(self, username, password):
        """Tentative de connexion optimisée pour instagrapi"""
        try:
            from instagrapi import Client

            client = Client()
            client.delay_range = [3, 7]

            client.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")

            print(f"🔐 Connexion instagrapi pour {username}...")

            client.login(username, password)

            try:
                user_id = client.user_id
                print(f"✅ Connexion instagrapi réussie! User ID: {user_id}")

                cookies_dict = client.get_cookies()
                cookies_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

                if username not in self.accounts:
                    self.accounts[username] = {}

                self.accounts[username].update({
                    'password': password,
                    'cookies': cookies_str,
                    'status': 'active',
                    'last_used': datetime.now().isoformat(),
                    'user_id': user_id
                })

                self.save_accounts()
                return client

            except Exception as e:
                print(f"❌ Erreur vérification connexion: {e}")
                return None

        except Exception as e:
            print(f"❌ Erreur connexion instagrapi: {e}")
            return None

    def get_instagrapi_client_from_cookies(self, username):
        """Crée un client instagrapi depuis les cookies sauvegardés"""
        try:
            from instagrapi import Client

            if username not in self.accounts:
                return None

            account_data = self.accounts[username]
            cookies_str = account_data.get('cookies', '')

            if not cookies_str:
                return None

            client = Client()
            client.delay_range = [3, 7]

            cookies_dict = {}
            for cookie in cookies_str.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies_dict[key.strip()] = value.strip()

            client.set_cookies(cookies_dict)

            try:
                client.get_timeline_feed()
                print(f"✅ Session restaurée pour {username}")
                return client
            except Exception:
                print(f"🔄 Session expirée pour {username}")
                return None

        except Exception as e:
            print(f"❌ Erreur création client depuis cookies: {e}")
            return None

    def get_advanced_headers(self, referer=None):
        """Headers avancés"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        if referer:
            headers['Referer'] = referer
        return headers

    def human_delay(self, min_seconds=2, max_seconds=5):
        """Délai humain"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def extract_csrf_token(self, html_content, session):
        """Extrait le CSRF token de multiple sources"""
        csrf_token = session.cookies.get('csrftoken')
        if csrf_token:
            return csrf_token

        patterns = [
            r'"csrf_token":"([^"]+)"',
            r"csrf_token\":\"([^\"]+)\"",
        ]

        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)

        return None

    def connect_instagram_account(self, username, password):
        """CONNEXION INSTAGRAM - VERSION CORRIGÉE"""
        print(f"🔐 Connexion Instagram pour {username}...")

        session = requests.Session()
        session.headers.update(self.get_advanced_headers())

        try:
            print("📄 Chargement page de connexion...")
            time.sleep(random.uniform(3, 6))

            login_response = session.get(
                'https://www.instagram.com/accounts/login/',
                timeout=30
            )

            if login_response.status_code != 200:
                print(f"❌ Erreur page login: {login_response.status_code}")
                return False

            csrf_token = self.extract_csrf_token(login_response.text, session)
            if not csrf_token:
                print("❌ CSRF token non trouvé")
                return False

            print(f"🔑 Token CSRF récupéré: {csrf_token[:10]}...")

            timestamp = int(time.time())
            enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"

            login_data = {
                'username': username,
                'enc_password': enc_password,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': '{}',
                'loginAttemptCount': 0
            }

            login_headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': '*/*',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459',
                'Origin': 'https://www.instagram.com',
                'Referer': 'https://www.instagram.com/accounts/login/',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }

            print("🚀 Envoi des identifiants...")
            time.sleep(random.uniform(2, 4))

            response = session.post(
                'https://www.instagram.com/accounts/login/ajax/',
                data=login_data,
                headers=login_headers,
                timeout=30
            )

            print(f"📊 Réponse serveur: {response.status_code}")

            if response.status_code != 200:
                print(f"🔍 Headers réponse: {dict(response.headers)}")
                if response.text:
                    print(f"🔍 Contenu réponse: {response.text[:200]}...")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"📦 Données réponse: {response_data}")

                    if response_data.get('authenticated'):
                        print(f"🎉 CONNEXION RÉUSSIE! User ID: {response_data.get('userId')}")
                        return self.save_successful_session(username, password, session, response_data)

                    else:
                        error_msg = response_data.get('message', 'Erreur inconnue')
                        error_type = response_data.get('error_type', 'N/A')
                        print(f"❌ Échec authentification: {error_type} - {error_msg}")
                        return False

                except Exception as json_error:
                    print(f"❌ Erreur analyse JSON: {json_error}")
                    return False

            elif response.status_code == 400:
                print("❌ ERREUR 400 - Mauvais format de requête")
                return False

            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print("❌ Timeout - Serveur trop lent à répondre")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Erreur de connexion - Vérifiez votre internet")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False

    def save_successful_session(self, username, password, session, response_data):
        """Sauvegarde la session après connexion réussie"""
        try:
            cookies_dict = dict(session.cookies)
            cookies_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

            if 'sessionid' not in cookies_str:
                print("⚠️ Cookie sessionid manquant")
                return False

            session_info = {
                'cookies': cookies_dict,
                'user_id': response_data.get('userId'),
                'authenticated_at': datetime.now().isoformat(),
                'status': 'active'
            }

            self.accounts[username] = {
                'password': password,
                'cookies': cookies_str,
                'session_data': json.dumps(session_info, ensure_ascii=False),
                'last_used': datetime.now().isoformat(),
                'status': 'active'
            }

            if self.save_accounts():
                print(f"💾 Compte {username} sauvegardé avec succès!")
                return True
            else:
                print("❌ Erreur lors de la sauvegarde fichier")
                return False

        except Exception as e:
            print(f"❌ Erreur sauvegarde session: {e}")
            return False

    def debug_connection(self, username, password):
        """Fonction de débug pour tester la connexion"""
        print("🔧 MODE DÉBUG CONNEXION")

        session = requests.Session()
        session.headers.update(self.get_advanced_headers())

        test_response = session.get('https://www.instagram.com/')
        print(f"✅ Test connexion: {test_response.status_code}")

        login_page = session.get('https://www.instagram.com/accounts/login/')
        print(f"✅ Page login: {login_page.status_code}")

        csrf_token = self.extract_csrf_token(login_page.text, session)
        print(f"✅ CSRF Token: {csrf_token}")

        timestamp = int(time.time())
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        print(f"✅ Format mot de passe: {enc_password[:50]}...")

        return True

    def display_accounts(self):
        """Affiche les comptes avec statut détaillé"""
        if not self.accounts:
            print("📭 Aucun compte enregistré")
            return

        print("\n" + "═" * 60)
        print("║               COMPTES INSTAGRAM - STATUT DÉTAILLÉ            ║")
        print("═" * 60)

        for i, (username, data) in enumerate(self.accounts.items(), 1):
            status = data.get('status', 'unknown')
            has_cookies = '✅' if data.get('cookies') else '❌'
            has_password = '✅' if data.get('password') else '❌'
            last_used = data.get('last_used', 'Jamais')[:10]

            status_icon = "✅" if status == "active" else "⚠️" if status == "problem" else "❌"

            print(f"│ {i:2d}. {username:<20} {status_icon} │ Cookies: {has_cookies} │ Pass: {has_password} │ {last_used:>10} │")

        print("═" * 60)
        print(f"📊 Total: {len(self.accounts)} compte(s)")

# INTERFACE UTILISATEUR
def main_menu():
    """Menu principal"""
    manager = AccountManager()

    while True:
        print("\n" + "═" * 50)
        print("║      GESTIONNAIRE COMPTES INSTAGRAM - INSTAGRAPi    ║")
        print("═" * 50)
        print(f"📁 Fichier: {manager.accounts_file}")
        print(f"👥 Comptes: {manager.get_account_count()}")

        active_info = manager.get_active_accounts_info()
        active_count = len([acc for acc in active_info if acc['has_cookies']])
        print(f"✅ Sessions actives: {active_count}")

        print("\n1. 📋 Afficher les comptes (détail)")
        print("2. ➕ Ajouter un compte (instagrapi)")
        print("3. 🔄 Tester connexion instagrapi")
        print("4. 🗑️ Supprimer un compte")
        print("5. 🚪 Quitter")

        choice = input("\n🎯 Choix: ").strip()

        if choice == "1":
            manager.display_accounts()

        elif choice == "2":
            print("\n👤 AJOUT COMPTE AVEC INSTAGRAPi")
            username = input("Nom d'utilisateur: ").strip()
            password = input("Mot de passe: ").strip()

            if username and password:
                print(f"\n[🔄] Connexion instagrapi pour {username}...")
                client = manager.connect_with_instagrapi(username, password)
                if client:
                    print(f"\n🎉 COMPTE {username} CONFIGURÉ POUR L'AUTOMATISATION!")
                else:
                    print(f"\n💔 Échec de la connexion instagrapi")
            else:
                print("❌ Identifiants manquants")

        elif choice == "3":
            print("\n🔧 TEST CONNEXION INSTAGRAPi")
            manager.display_accounts()
            if manager.accounts:
                username = input("Nom d'utilisateur à tester: ").strip()
                if username in manager.accounts:
                    client = manager.get_instagrapi_client_from_cookies(username)
                    if client:
                        print("✅ Session instagrapi VALIDE!")
                    else:
                        print("❌ Session invalide, tentative reconnexion...")
                        password = manager.accounts[username].get('password')
                        if password:
                            manager.connect_with_instagrapi(username, password)
                        else:
                            print("❌ Mot de passe manquant")
                else:
                    print("❌ Compte non trouvé")
            else:
                print("📭 Aucun compte")

        elif choice == "4":
            manager.display_accounts()
            if manager.accounts:
                try:
                    index = int(input("\nNuméro du compte à supprimer: ")) - 1
                    accounts = list(manager.accounts.keys())
                    if 0 <= index < len(accounts):
                        username = accounts[index]
                        if manager.delete_account(username):
                            print("✅ Compte supprimé")
                    else:
                        print("❌ Numéro invalide")
                except ValueError:
                    print("❌ Veuillez entrer un nombre")
            else:
                print("📭 Aucun compte à supprimer")

        elif choice == "5":
            print("👋 Au revoir!")
            break

        else:
            print("❌ Choix invalide")

        input("\n↵ Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main_menu()
