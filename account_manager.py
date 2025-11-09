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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

    def load_accounts(self):
        """Charge les comptes depuis le fichier JSON"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                    print(f"✅ {len(accounts_data)} compte(s) chargé(s) depuis {self.accounts_file}")
                    return accounts_data
            except Exception as e:
                print(f"❌ Erreur chargement comptes: {e}")
                return {}
        else:
            print(f"📁 Fichier {self.accounts_file} non trouvé, création...")
            return {}

    def save_accounts(self):
        """Sauvegarde les comptes dans le fichier JSON"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
            print(f"💾 {len(self.accounts)} compte(s) sauvegardé(s) dans {self.accounts_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde comptes: {e}")
            return False

    def get_advanced_headers(self, referer=None):
        """Headers avancés pour éviter la détection"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        return headers

    def human_delay(self, min_seconds=2, max_seconds=5):
        """Délai humain aléatoire"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def extract_csrf_token(self, html_content, session):
        """Extrait le CSRF token de multiple sources"""
        # Depuis les cookies
        csrf_token = session.cookies.get('csrftoken')
        if csrf_token:
            return csrf_token

        # Depuis le HTML
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
        """
        CONNEXION INSTAGRAM - VERSION CORRIGÉE POUR ERREUR 400
        """
        print(f"🔐 Connexion Instagram pour {username}...")

        session = requests.Session()
        session.headers.update(self.get_advanced_headers())

        try:
            # ÉTAPE 1: Page de login avec plus de délai
            print("📄 Chargement page de connexion...")
            time.sleep(random.uniform(3, 6))

            login_response = session.get(
                'https://www.instagram.com/accounts/login/',
                timeout=30
            )

            if login_response.status_code != 200:
                print(f"❌ Erreur page login: {login_response.status_code}")
                return False

            # ÉTAPE 2: Extraction CSRF Token améliorée
            csrf_token = self.extract_csrf_token(login_response.text, session)
            if not csrf_token:
                print("❌ CSRF token non trouvé")
                return False

            print(f"🔑 Token CSRF récupéré: {csrf_token[:10]}...")

            # ÉTAPE 3: Format de mot de passe CORRECT pour éviter 400
            timestamp = int(time.time())
            enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"

            # Données de connexion CORRIGÉES
            login_data = {
                'username': username,
                'enc_password': enc_password,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'trustedDeviceRecords': '{}',
                'loginAttemptCount': 0
            }

            # ÉTAPE 4: Headers CORRIGÉS pour éviter 400
            login_headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': '*/*',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459',  # CRITIQUE
                'Origin': 'https://www.instagram.com',
                'Referer': 'https://www.instagram.com/accounts/login/',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }

            # ÉTAPE 5: Connexion avec plus de délai
            print("🚀 Envoi des identifiants...")
            time.sleep(random.uniform(2, 4))

            response = session.post(
                'https://www.instagram.com/accounts/login/ajax/',
                data=login_data,
                headers=login_headers,
                timeout=30
            )

            print(f"📊 Réponse serveur: {response.status_code}")

            # AFFICHER PLUS D'INFOS POUR DEBUG
            if response.status_code != 200:
                print(f"🔍 Headers réponse: {dict(response.headers)}")
                if response.text:
                    print(f"🔍 Contenu réponse: {response.text[:200]}...")

            # ÉTAPE 6: Analyse réponse
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
                print("💡 Instagram a rejeté la requête de connexion")
                print("🔧 Vérifiez le format du mot de passe et les headers")
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
            # Conversion cookies
            cookies_dict = dict(session.cookies)
            cookies_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

            # Vérification cookies essentiels
            if 'sessionid' not in cookies_str:
                print("⚠️ Cookie sessionid manquant")
                return False

            # Données de session
            session_info = {
                'cookies': cookies_dict,
                'user_id': response_data.get('userId'),
                'authenticated_at': datetime.now().isoformat(),
                'status': 'active'
            }

            # Sauvegarde compte
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

    # CORRECTION : Méthodes manquantes ajoutées
    def get_active_accounts(self):
        """Retourne tous les comptes actifs - CORRIGÉ"""
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
        """Retourne un compte aléatoire actif"""
        active_accounts = self.get_active_accounts()
        if active_accounts:
            return random.choice(active_accounts)
        return None

    def get_account_by_username(self, username):
        """Retourne un compte spécifique par username"""
        return self.accounts.get(username)

    def check_single_account_status(self, username):
        """Vérifie le statut d'un compte - CORRIGÉ"""
        if username in self.accounts:
            account_data = self.accounts[username]
            cookies = account_data.get('cookies', '')
            status = account_data.get('status', 'unknown')

            if cookies and 'sessionid' in cookies and status == 'active':
                return "active"
            return "no_session"
        return "not_found"

    def add_account(self, username, password, cookies="", session_data=""):
        """Ajoute un compte manuellement"""
        self.accounts[username] = {
            'password': password,
            'cookies': cookies,
            'session_data': session_data,
            'last_used': datetime.now().isoformat(),
            'status': 'active'
        }
        return self.save_accounts()

    def get_all_accounts(self):
        """Retourne tous les comptes actifs"""
        active_accounts = []
        for username, data in self.accounts.items():
            if data.get('status') != 'inactive':
                active_accounts.append((
                    username,
                    data.get('cookies', ''),
                    data.get('session_data', '')
                ))
        return active_accounts

    def display_accounts(self):
        """Affiche tous les comptes avec statut détaillé"""
        if not self.accounts:
            print("📭 Aucun compte enregistré")
            return

        print("\n" + "═" * 50)
        print("║          COMPTES INSTAGRAM - STATUT         ║")
        print("═" * 50)

        for i, (username, data) in enumerate(self.accounts.items(), 1):
            status = self.check_single_account_status(username)
            status_icon = "✅" if status == "active" else "❌"
            last_used = data.get('last_used', 'Jamais')

            if len(last_used) > 10:
                last_used = last_used[:10]

            print(f"│ {i:2d}. {username:<20} {status_icon} {last_used:>10} │")

        print("═" * 50)
        print(f"📊 Total: {len(self.accounts)} compte(s)")

    def delete_account(self, username):
        """Supprime un compte"""
        if username in self.accounts:
            del self.accounts[username]
            if self.save_accounts():
                print(f"✅ Compte {username} supprimé")
                return True
        print(f"❌ Compte {username} non trouvé")
        return False

    def get_account_count(self):
        """Retourne le nombre de comptes"""
        return len(self.accounts)

    def debug_connection(self, username, password):
        """Fonction de débug pour tester la connexion"""
        print("🔧 MODE DÉBUG CONNEXION")

        session = requests.Session()
        session.headers.update(self.get_advanced_headers())

        # Test connexion basique
        test_response = session.get('https://www.instagram.com/')
        print(f"✅ Test connexion: {test_response.status_code}")

        # Test page login
        login_page = session.get('https://www.instagram.com/accounts/login/')
        print(f"✅ Page login: {login_page.status_code}")

        # Extraction CSRF
        csrf_token = self.extract_csrf_token(login_page.text, session)
        print(f"✅ CSRF Token: {csrf_token}")

        # Test format mot de passe
        timestamp = int(time.time())
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        print(f"✅ Format mot de passe: {enc_password[:50]}...")

        return True

# Interface utilisateur
def main_menu():
    """Menu principal"""
    manager = AccountManager()

    while True:
        print("\n" + "═" * 40)
        print("║    GESTIONNAIRE COMPTES INSTAGRAM    ║")
        print("═" * 40)
        print(f"📁 Fichier: {manager.accounts_file}")
        print(f"👥 Comptes: {manager.get_account_count()}")
        print("\n1. 📋 Afficher les comptes")
        print("2. ➕ Ajouter un compte")
        print("3. 🗑️ Supprimer un compte")
        print("4. 🔧 Tester connexion (débug)")
        print("5. 🚪 Quitter")

        choice = input("\n🎯 Choix: ").strip()

        if choice == "1":
            manager.display_accounts()

        elif choice == "2":
            print("\n👤 AJOUT D'UN COMPTE INSTAGRAM")
            username = input("Nom d'utilisateur: ").strip()
            password = input("Mot de passe: ").strip()

            if username and password:
                print(f"\n[ℹ️] Connexion pour {username}...")
                success = manager.connect_instagram_account(username, password)
                if success:
                    print(f"\n🎉 COMPTE {username} PRÊT À UTILISER!")
                else:
                    print(f"\n💔 Échec de la connexion")
            else:
                print("❌ Identifiants manquants")

        elif choice == "3":
            manager.display_accounts()
            if manager.get_account_count() > 0:
                try:
                    index = int(input("\nNuméro du compte à supprimer: ")) - 1
                    accounts = list(manager.accounts.keys())
                    if 0 <= index < len(accounts):
                        username = accounts[index]
                        if manager.delete_account(username):
                            print("✅ Compte supprimé")
                        else:
                            print("❌ Erreur suppression")
                    else:
                        print("❌ Numéro invalide")
                except ValueError:
                    print("❌ Veuillez entrer un nombre")
            else:
                print("📭 Aucun compte à supprimer")

        elif choice == "4":
            print("\n🔧 MODE DÉBUG CONNEXION")
            username = input("Nom d'utilisateur: ").strip()
            password = input("Mot de passe: ").strip()

            if username and password:
                manager.debug_connection(username, password)
            else:
                print("❌ Identifiants manquants")

        elif choice == "5":
            print("👋 Au revoir!")
            break

        else:
            print("❌ Choix invalide")

        input("\n↵ Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main_menu()
