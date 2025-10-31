# instagram_session.py - VERSION CORRIGÉE
import requests
import json
import time
import random
import re
from datetime import datetime, timedelta
from account_manager import AccountManager

class InstagramSessionManager:
    def __init__(self):
        self.sessions = {}
        self.account_manager = AccountManager()

    def get_advanced_headers(self):
        """Headers complets pour contourner les protections Instagram"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def get_session(self, username, cookies_str=None):
        """
        Récupère ou crée une session Instagram pour un compte
        """
        # Vérifier si on a déjà une session valide
        if username in self.sessions:
            session_data = self.sessions[username]
            if self.is_session_valid(session_data):
                return session_data['session']

        # Essayer de charger depuis account_manager
        account_data = self.account_manager.accounts.get(username, {})
        session_json = account_data.get('session_data', '')

        if session_json:
            try:
                session_data = json.loads(session_json)
                if self.is_session_valid(session_data):
                    session = self.create_session_from_data(session_data)
                    self.sessions[username] = {
                        'session': session,
                        'created_at': session_data['created_at'],
                        'cookies': session_data['cookies']
                    }
                    return session
            except Exception as e:
                print(f"❌ Erreur chargement session {username}: {e}")

        # Sinon, créer une nouvelle session
        return self.create_new_session(username)

    def create_new_session(self, username):
        """
        Crée une nouvelle session Instagram avec contournement des protections
        """
        password = self.account_manager.get_password(username)
        if not password:
            print(f"❌ Mot de passe manquant pour {username}")
            return None

        print(f"🔄 Création nouvelle session pour {username}...")

        session = requests.Session()
        session.headers.update(self.get_advanced_headers())

        try:
            # ÉTAPE 1: Récupérer la page de login
            print("📄 Récupération page login...")
            time.sleep(random.uniform(2, 4))

            login_page = session.get(
                'https://www.instagram.com/accounts/login/',
                timeout=30,
                allow_redirects=True
            )

            if login_page.status_code != 200:
                print(f"❌ Erreur page login: {login_page.status_code}")
                return None

            # Extraire le CSRF token
            csrf_token = self.extract_csrf_token(login_page.text, session)
            if not csrf_token:
                print("❌ Impossible d'extraire le CSRF token")
                return None

            print(f"🔑 CSRF Token: {csrf_token[:20]}...")

            # ÉTAPE 2: Préparer la connexion
            print("🔐 Préparation connexion...")
            time.sleep(random.uniform(1, 3))

            # Format du mot de passe encrypté
            enc_password = self.create_enc_password(password)

            login_data = {
                'username': username,
                'enc_password': enc_password,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': '{}'
            }

            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'Referer': 'https://www.instagram.com/accounts/login/',
                'Origin': 'https://www.instagram.com'
            }

            # ÉTAPE 3: Envoyer la requête de connexion
            print("📡 Envoi requête connexion...")
            login_response = session.post(
                'https://www.instagram.com/accounts/login/ajax/',
                data=login_data,
                headers=login_headers,
                timeout=30,
                allow_redirects=False
            )

            print(f"📊 Code HTTP: {login_response.status_code}")

            if login_response.status_code == 200:
                try:
                    response_data = login_response.json()

                    if response_data.get('authenticated'):
                        print(f"✅ Connexion réussie pour {username}")

                        # Vérifier que la session est valide
                        if self.verify_session(session):
                            # Sauvegarder la session
                            session_data = {
                                'cookies': dict(session.cookies),
                                'created_at': datetime.now().isoformat(),
                                'user_agent': session.headers['User-Agent']
                            }

                            self.sessions[username] = {
                                'session': session,
                                'created_at': session_data['created_at'],
                                'cookies': session_data['cookies']
                            }

                            self.save_session_to_account(username, session_data)
                            print(f"💾 Session sauvegardée pour {username}")
                            return session
                        else:
                            print("❌ Session non valide après connexion")
                    else:
                        error_msg = response_data.get('message', 'Erreur inconnue')
                        print(f"❌ Authentification échouée: {error_msg}")
                        if 'checkpoint' in error_msg.lower():
                            print("🚫 Vérification de sécurité requise")

                except Exception as e:
                    print(f"❌ Erreur parsing réponse: {e}")
            else:
                print(f"❌ Erreur HTTP connexion: {login_response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ Timeout lors de la connexion")
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")

        return None

    def extract_csrf_token(self, html_content, session):
        """Extrait le CSRF token de différentes manières"""
        # Méthode 1: Depuis le JSON dans le HTML
        pattern1 = r'"csrf_token":"([^"]+)"'
        match1 = re.search(pattern1, html_content)
        if match1:
            return match1.group(1)

        # Méthode 2: Depuis les cookies
        csrf_cookie = session.cookies.get('csrftoken')
        if csrf_cookie:
            return csrf_cookie

        # Méthode 3: Depuis les meta tags
        pattern3 = r'<meta name="csrf-token" content="([^"]+)"'
        match3 = re.search(pattern3, html_content)
        if match3:
            return match3.group(1)

        return None

    def create_enc_password(self, password):
        """Crée le mot de passe encrypté pour Instagram"""
        timestamp = int(time.time())
        return f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}'

    def verify_session(self, session):
        """Vérifie que la session est valide"""
        try:
            test_response = session.get(
                'https://www.instagram.com/accounts/edit/',
                timeout=15,
                allow_redirects=True
            )

            # Si on est redirigé vers login, session invalide
            if 'accounts/login' in test_response.url:
                return False

            return test_response.status_code == 200
        except:
            return False

    def is_session_valid(self, session_data):
        """
        Vérifie si une session est encore valide
        """
        try:
            created_at = datetime.fromisoformat(session_data['created_at'])
            # Une session est valide pendant 12 heures
            if datetime.now() - created_at > timedelta(hours=12):
                return False

            # Tester la session
            session = self.create_session_from_data(session_data)
            return self.verify_session(session)

        except:
            return False

    def create_session_from_data(self, session_data):
        """
        Recrée une session requests à partir des données sauvegardées
        """
        session = requests.Session()
        session.cookies.update(session_data['cookies'])
        session.headers.update({
            'User-Agent': session_data.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        })
        return session

    def save_session_to_account(self, username, session_data):
        """
        Sauvegarde la session dans account_manager
        """
        self.account_manager.update_session(username, json.dumps(session_data))

        # Sauvegarder aussi les cookies au format string
        cookies_str = '; '.join([f"{k}={v}" for k, v in session_data['cookies'].items()])
        self.account_manager.update_cookies(username, cookies_str)

    def refresh_all_sessions(self):
        """
        Rafraîchit toutes les sessions expirées
        """
        print("🔄 Rafraîchissement des sessions Instagram...")
        accounts = self.account_manager.get_all_accounts()

        success_count = 0
        for username, cookies, session_data in accounts:
            if self.get_session(username):
                success_count += 1
            else:
                print(f"❌ Impossible de rafraîchir {username}")

        print(f"📊 Sessions rafraîchies: {success_count}/{len(accounts)}")
