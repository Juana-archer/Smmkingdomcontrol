import json
import os
import requests
import time
import re
import random
from datetime import datetime
from pathlib import Path

class AccountManager:
    def __init__(self, accounts_file="instagram_accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = self.load_accounts()
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/115.0 Firefox/115.0',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]

    # ======================================================
    # NOUVELLE MÉTHODE : NETTOYAGE COOKIES
    # ======================================================

    def clean_duplicate_cookies(self, session):
        """Nettoie les cookies dupliqués dans la session"""
        try:
            # Créer un nouveau cookiejar sans doublons
            clean_cookies = {}
            for cookie in session.cookies:
                clean_cookies[cookie.name] = cookie.value
            
            # Recréer la session avec cookies propres
            session.cookies.clear()
            for name, value in clean_cookies.items():
                session.cookies.set(name, value)
                
            return True
        except Exception as e:
            print(f"⚠️ Erreur nettoyage cookies: {e}")
            return False

    # ======================================================
    # MÉTHODES PRINCIPALES POUR INSTAGRAM_TASKS.PY
    # ======================================================

    def get_requests_session_for_tasks(self, username):
        """MÉTHODE PRINCIPALE - Fournit session requests pour instagram_tasks.py - VERSION CORRIGÉE"""
        print(f"🔍 Récupération session requests pour {username}")
        
        # Vérifier si le compte existe
        if username not in self.accounts:
            print(f"❌ Compte {username} non trouvé")
            return None
        
        # Charger la session existante
        session = self.load_session_requests(username)
        if session and self.session_valid_requests(session):
            # ✅ NETTOYER LES COOKIES AVANT UTILISATION
            self.clean_duplicate_cookies(session)
            print(f"✅ Session requests valide pour {username}")
            return session
        
        # Si session invalide, essayer de reconnecter
        password = self.accounts[username].get('password')
        if password:
            print(f"🔄 Reconnexion nécessaire pour {username}")
            success, new_session = self.login_instagram_requests(username, password)
            if success:
                # ✅ NETTOYER LES COOKIES DE LA NOUVELLE SESSION
                self.clean_duplicate_cookies(new_session)
                return new_session
        
        print(f"❌ Impossible d'obtenir session pour {username}")
        return None

    def load_session_requests(self, username):
        """Charge une session requests existante"""
        if username not in self.accounts:
            return None

        account_data = self.accounts[username]
        cookies_str = account_data.get('cookies', '')
        
        if not cookies_str:
            return None

        session = requests.Session()
        try:
            # Ajouter les cookies correctement
            cookies_dict = {}
            for cookie in cookies_str.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies_dict[key.strip()] = value.strip()
            
            # Mettre à jour la session avec tous les cookies
            session.cookies.update(cookies_dict)
            
            # Ajouter des headers par défaut
            session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
            })
            
            return session
            
        except Exception as e:
            print(f"❌ Erreur chargement session requests: {e}")
            return None

    def session_valid_requests(self, session):
        """Test validité session requests"""
        try:
            # Essayer plusieurs endpoints pour plus de fiabilité
            endpoints = [
                "https://www.instagram.com/api/v1/accounts/current_user/?edit=true",
                "https://www.instagram.com/api/v1/feed/timeline/",
            ]
            
            for endpoint in endpoints:
                try:
                    headers = {
                        "User-Agent": random.choice(self.user_agents),
                        "Accept": "application/json",
                        "X-IG-App-ID": "936619743392459"
                    }
                    r = session.get(endpoint, headers=headers, timeout=20)
                    
                    if r.status_code == 200:
                        return True
                        
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur validation session: {e}")
            return False

    # ======================================================
    # CONNEXION INSTAGRAM VIA REQUESTS
    # ======================================================

    def base_headers(self, csrf=""):
        """Headers navigateur pour anti-ban"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "*/*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-CSRFToken": csrf,
            "X-Requested-With": "XMLHttpRequest",
            "X-Instagram-AJAX": "1007892310",
            "X-IG-App-ID": "936619743392459",
            "Referer": "https://www.instagram.com/accounts/login/",
            "Origin": "https://www.instagram.com",
        }

    def pre_login(self, session):
        """Récupérer csrftoken + mid avant login"""
        url = "https://www.instagram.com/accounts/login/"
        try:
            r = session.get(url, headers={"User-Agent": random.choice(self.user_agents)}, timeout=30)
            r.raise_for_status()
            
            csrf = session.cookies.get("csrftoken", "")
            mid = session.cookies.get("mid", "")
            
            if not csrf:
                print("⚠️ CSRF token non trouvé dans les cookies")
                
            return csrf, mid
        except Exception as e:
            print(f"❌ Erreur pre-login: {e}")
            return None, None

    def login_instagram_requests(self, username, password):
        """Login réel avec password formaté - Version requests"""
        print(f"🔐 Connexion requests pour {username}...")
        
        session = requests.Session()
        csrf, mid = self.pre_login(session)
        
        if not csrf:
            print("❌ Impossible de récupérer le CSRF token")
            return False, None

        time.sleep(random.uniform(1.5, 3.5))

        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}"
        payload = {
            "username": username,
            "enc_password": enc_password,
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "trustedDeviceRecords": "{}"
        }

        try:
            r = session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                data=payload,
                headers=self.base_headers(csrf),
                allow_redirects=True,
                timeout=30
            )

            try:
                data = r.json()
            except:
                print(f"❌ Réponse non JSON: {r.text[:200]}")
                return False, None

            print(f"📊 Réponse authentification: {data}")

            if data.get("authenticated") and data.get("status") == "ok":
                print(f"✅ Login requests réussi! User ID: {data.get('userId')}")
                self.save_session_requests(username, session, data)
                return True, session

            else:
                error_msg = data.get('message', 'Erreur inconnue')
                error_type = data.get('error_type', 'N/A')
                print(f"❌ Échec authentification requests: {error_type} - {error_msg}")
                return False, None

        except Exception as e:
            print(f"❌ Erreur lors du login requests: {e}")
            return False, None

    def save_session_requests(self, username, session, response_data=None):
        """Sauvegarde la session requests"""
        try:
            cookies_dict = session.cookies.get_dict()
            cookies_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
            
            session_info = {
                'cookies': cookies_dict,
                'authenticated_at': datetime.now().isoformat(),
                'method': 'requests',
                'user_id': response_data.get('userId') if response_data else None
            }

            if username not in self.accounts:
                self.accounts[username] = {}

            self.accounts[username].update({
                'cookies': cookies_str,
                'session_data': json.dumps(session_info, ensure_ascii=False),
                'last_used': datetime.now().isoformat(),
                'status': 'active'
            })

            if self.save_accounts():
                print(f"💾 Session requests sauvegardée pour {username}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde session requests: {e}")
            return False

    # ======================================================
    # MÉTHODES DE GESTION DES COMPTES (CONSERVÉES)
    # ======================================================

    def load_accounts(self):
        """Charge les comptes depuis le fichier JSON"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                    print(f"✅ {len(accounts_data)} compte(s) chargé(s)")

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

    def get_all_accounts(self):
        return self.accounts

    def get_account_count(self):
        return len(self.accounts)

    def get_active_accounts(self):
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
        active_accounts = self.get_active_accounts()
        if active_accounts:
            return random.choice(active_accounts)
        return None

    def get_account_by_username(self, username):
        return self.accounts.get(username)

    def check_single_account_status(self, username):
        if username in self.accounts:
            account_data = self.accounts[username]
            cookies = account_data.get('cookies', '')
            status = account_data.get('status', 'unknown')

            if cookies and 'sessionid' in cookies and status == 'active':
                return "active"
            return "no_session"
        return "not_found"

    def add_account(self, username, password, cookies="", session_data=""):
        self.accounts[username] = {
            'password': password,
            'cookies': cookies,
            'session_data': session_data,
            'last_used': datetime.now().isoformat(),
            'status': 'active'
        }
        return self.save_accounts()

    def delete_account(self, username):
        if username in self.accounts:
            del self.accounts[username]
            if self.save_accounts():
                print(f"✅ Compte {username} supprimé")
                return True
        print(f"❌ Compte {username} non trouvé")
        return False

    def get_all_usernames(self):
        return list(self.accounts.keys())

    def update_account_cookies(self, username, cookies_str):
        if username in self.accounts:
            self.accounts[username]['cookies'] = cookies_str
            self.accounts[username]['last_used'] = datetime.now().isoformat()
            return self.save_accounts()
        return False

    def validate_session(self, username):
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
        if username in self.accounts:
            self.accounts[username]['status'] = 'problem'
            self.accounts[username]['last_error'] = reason
            self.accounts[username]['error_time'] = datetime.now().isoformat()
            self.save_accounts()
            print(f"🚫 Compte {username} marqué comme problématique: {reason}")

    def reactivate_account(self, username):
        if username in self.accounts:
            self.accounts[username]['status'] = 'active'
            if 'last_error' in self.accounts[username]:
                del self.accounts[username]['last_error']
            self.save_accounts()
            print(f"✅ Compte {username} réactivé")

    def display_accounts(self):
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

# INTERFACE UTILISATEUR SIMPLIFIÉE
def main_menu():
    """Menu principal"""
    manager = AccountManager()

    while True:
        print("\n" + "═" * 50)
        print("║      GESTIONNAIRE COMPTES INSTAGRAM - REQUESTS    ║")
        print("═" * 50)
        print(f"📁 Fichier: {manager.accounts_file}")
        print(f"👥 Comptes: {manager.get_account_count()}")

        print("\n1. 📋 Afficher les comptes")
        print("2. 🔐 Ajouter un compte (requests)")
        print("3. 🧪 Tester session")
        print("4. 🗑️ Supprimer un compte")
        print("5. 🚪 Quitter")

        choice = input("\n🎯 Choix: ").strip()

        if choice == "1":
            manager.display_accounts()

        elif choice == "2":
            print("\n👤 AJOUT COMPTE AVEC REQUESTS")
            username = input("Nom d'utilisateur: ").strip()
            password = input("Mot de passe: ").strip()

            if username and password:
                success, session = manager.login_instagram_requests(username, password)
                if success:
                    print(f"🎉 COMPTE {username} AJOUTÉ AVEC SUCCÈS!")
                else:
                    print(f"❌ Échec de la connexion")
            else:
                print("❌ Identifiants manquants")

        elif choice == "3":
            print("\n🧪 TEST SESSION REQUESTS")
            manager.display_accounts()
            if manager.accounts:
                username = input("Nom d'utilisateur à tester: ").strip()
                if username in manager.accounts:
                    session = manager.load_session_requests(username)
                    if session and manager.session_valid_requests(session):
                        print("✅ Session requests VALIDE!")
                    else:
                        print("❌ Session requests invalide ou expirée")
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
