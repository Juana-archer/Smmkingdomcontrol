# account_manager.py - VERSION COMPLÈTE ET CORRIGÉE
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

    def load_accounts(self):
        """Charge les comptes depuis le fichier JSON"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_accounts(self):
        """Sauvegarde les comptes dans le fichier JSON"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde comptes: {e}")
            return False

    def add_account(self, username, password, cookies="", session_data=""):
        """Ajoute un compte avec session"""
        self.accounts[username] = {
            'password': password,
            'cookies': cookies,
            'session_data': session_data,
            'last_used': datetime.now().isoformat(),
            'status': 'active'
        }
        return self.save_accounts()

    def get_all_accounts(self):
        """Retourne tous les comptes actifs - FORMAT COMPATIBLE"""
        active_accounts = []
        for username, data in self.accounts.items():
            if data.get('status') != 'inactive':
                # Format: (username, cookies_string, session_data_string)
                active_accounts.append((
                    username,
                    data.get('cookies', ''),
                    data.get('session_data', '')
                ))
        return active_accounts

    def get_password(self, username):
        """Retourne le mot de passe d'un compte"""
        return self.accounts.get(username, {}).get('password')

    def update_cookies(self, username, cookies):
        """Met à jour les cookies d'un compte"""
        if username in self.accounts:
            self.accounts[username]['cookies'] = cookies
            self.accounts[username]['last_used'] = datetime.now().isoformat()
            return self.save_accounts()
        return False

    def update_session(self, username, session_data):
        """Met à jour la session complète"""
        if username in self.accounts:
            self.accounts[username]['session_data'] = session_data
            self.accounts[username]['last_used'] = datetime.now().isoformat()
            return self.save_accounts()
        return False

    def mark_problem_account(self, username):
        """Marque un compte comme problématique"""
        if username in self.accounts:
            self.accounts[username]['status'] = 'problem'
            return self.save_accounts()
        return False

    def get_account_count(self):
        """Retourne le nombre de comptes"""
        return len(self.get_all_accounts())

    def display_accounts(self):
        """Affiche tous les comptes"""
        accounts = self.get_all_accounts()
        if not accounts:
            print("📭 Aucun compte enregistré")
            return

        print("╔════════════════════════════════════════╗")
        print("║          COMPTES INSTAGRAM            ║")
        print("╠════════════════════════════════════════╣")

        for i, (username, cookies, session_data) in enumerate(accounts, 1):
            status = "✅ ACTIF" if cookies else "❌ INACTIF"
            print(f"║ {i:2d}. {username:<20} {status} ║")

        print("╚════════════════════════════════════════╝")
        print(f"📊 Total: {len(accounts)} compte(s)")

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

    def connect_instagram_account(self, username, password):
        """
        Nouvelle méthode de connexion avec contournement des protections
        """
        print(f"🔐 Connexion Instagram pour {username}...")

        # Sauvegarder d'abord le compte avec le mot de passe
        self.add_account(username, password, "", "")

        try:
            session = requests.Session()
            session.headers.update(self.get_advanced_headers())

            # ÉTAPE 1: Récupérer la page de login avec délai
            print("📄 Récupération page login...")
            time.sleep(random.uniform(2, 4))

            login_page = session.get(
                'https://www.instagram.com/accounts/login/',
                timeout=30,
                allow_redirects=True
            )

            if login_page.status_code != 200:
                print(f"❌ Erreur page login: {login_page.status_code}")
                return False

            # Extraire le CSRF token
            csrf_token = self.extract_csrf_token(login_page.text, session)
            if not csrf_token:
                print("❌ Impossible d'extraire le CSRF token")
                return None

            print(f"🔑 CSRF Token récupéré")

            # ÉTAPE 2: Préparer la connexion
            print("🔐 Préparation connexion...")
            time.sleep(random.uniform(1, 3))

            # Format du mot de passe encrypté pour Instagram
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
                            # Préparer les données de session
                            session_data = {
                                'cookies': dict(session.cookies),
                                'created_at': datetime.now().isoformat(),
                                'user_agent': session.headers['User-Agent']
                            }

                            # Sauvegarder les cookies au format string
                            cookies_str = '; '.join([f"{k}={v}" for k, v in session.cookies.items()])

                            # Mettre à jour le compte avec les cookies
                            self.update_cookies(username, cookies_str)
                            self.update_session(username, json.dumps(session_data))

                            print(f"💾 Session sauvegardée pour {username}")
                            return True
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

        # En cas d'échec, supprimer le compte
        if username in self.accounts:
            del self.accounts[username]
            self.save_accounts()

        return False

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

    def delete_account(self, username):
        """Supprime un compte"""
        if username in self.accounts:
            del self.accounts[username]
            if self.save_accounts():
                print(f"✅ Compte {username} supprimé")
                return True
        print(f"❌ Compte {username} non trouvé")
        return False

    def get_random_account(self):
        """Retourne un compte aléatoire"""
        accounts = self.get_all_accounts()
        return random.choice(accounts) if accounts else None

    def validate_account(self, username):
        """Valide qu'un compte a des cookies valides"""
        account_data = self.accounts.get(username, {})
        cookies_str = account_data.get('cookies', '')
        return bool(cookies_str and 'sessionid' in cookies_str)

    def get_account_info(self, username):
        """Retourne les informations d'un compte"""
        return self.accounts.get(username, {})

# Fonction utilitaire pour faciliter la migration
def migrate_from_old_format(manager, old_accounts_file):
    """
    Migre les comptes depuis l'ancien format
    """
    if not os.path.exists(old_accounts_file):
        print("📭 Aucun ancien fichier trouvé")
        return

    try:
        migrated_count = 0
        with open(old_accounts_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        if '|' in line:
                            username, cookies_str = line.split('|', 1)
                            # Ajouter le compte sans mot de passe
                            if manager.add_account(username, "", cookies_str, ""):
                                migrated_count += 1
                                print(f"✅ Migré: {username}")
                    except Exception as e:
                        print(f"❌ Erreur migration {line}: {e}")

        print(f"📊 Migration terminée: {migrated_count} compte(s) migré(s)")
    except Exception as e:
        print(f"❌ Erreur lecture ancien fichier: {e}")

# Interface utilisateur simple
def main_menu():
    """Menu principal pour gérer les comptes"""
    manager = AccountManager()

    while True:
        print("\n" + "="*50)
        print("       GESTIONNAIRE DE COMPTES INSTAGRAM")
        print("="*50)
        print(f"📁 Fichier: {manager.accounts_file}")
        print(f"👥 Comptes: {manager.get_account_count()}")
        print("\n1. 📋 Afficher les comptes")
        print("2. ➕ Ajouter un compte")
        print("3. 🗑️ Supprimer un compte")
        print("4. 🔄 Migrer depuis ancien format")
        print("5. 🚪 Quitter")

        choice = input("\n📝 Choix: ").strip()

        if choice == "1":
            manager.display_accounts()

        elif choice == "2":
            print("\n👤 AJOUTER UN COMPTE INSTAGRAM")
            username = input("[?] Nom d'utilisateur Instagram: ").strip()
            password = input("[🔒] Mot de passe Instagram: ").strip()

            if username and password:
                print(f"\n[ℹ️] Résumé du compte:")
                print(f"   Utilisateur: {username}")
                print(f"   Mot de passe: {'*' * len(password)}")

                confirm = input("[?] Confirmer l'ajout? (o/n): ").strip().lower()
                if confirm == 'o':
                    success = manager.connect_instagram_account(username, password)
                    if success:
                        print("🎉 Compte ajouté avec succès!")
                    else:
                        print("💔 Échec de l'ajout du compte")
                else:
                    print("❌ Ajout annulé")
            else:
                print("❌ Nom d'utilisateur et mot de passe requis")

        elif choice == "3":
            manager.display_accounts()
            if manager.get_account_count() > 0:
                try:
                    index = int(input("\n[?] Numéro du compte à supprimer: ")) - 1
                    accounts = manager.get_all_accounts()
                    if 0 <= index < len(accounts):
                        username = accounts[index][0]
                        if manager.delete_account(username):
                            print("✅ Compte supprimé")
                        else:
                            print("❌ Erreur suppression")
                    else:
                        print("❌ Numéro invalide")
                except ValueError:
                    print("❌ Veuillez entrer un nombre")

        elif choice == "4":
            old_file = input("[?] Chemin de l'ancien fichier: ").strip()
            if old_file:
                migrate_from_old_format(manager, old_file)
            else:
                print("❌ Chemin invalide")

        elif choice == "5":
            print("👋 Au revoir!")
            break

        else:
            print("❌ Choix invalide")

        input("\n[↵] Appuyez sur Entrée pour continuer...")

# Test et utilisation
if __name__ == "__main__":
    main_menu()
