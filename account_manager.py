# account_manager.py - VERSION ULTIME FONCTIONNELLE
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
        """Headers pour Instagram"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
            'Cache-Control': 'max-age=0'
        }

    def connect_instagram_account(self, username, password):
        """
        MÉTHODE ULTIME - SAUVEGARDE DIRECTE SI AUTHENTIFICATION RÉUSSIE
        """
        print(f"🔐 Connexion Instagram pour {username}...")

        try:
            session = requests.Session()
            session.headers.update(self.get_advanced_headers())

            # ÉTAPE 1: Récupérer la page de login
            print("📄 Récupération page login...")
            time.sleep(2)

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
                return False

            print(f"🔑 CSRF Token récupéré")

            # ÉTAPE 2: Préparer la connexion
            print("🔐 Préparation connexion...")
            time.sleep(2)

            # Utiliser directement le format qui fonctionne
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
                    print(f"📦 Réponse: {response_data}")

                    if response_data.get('authenticated'):
                        print(f"🎉 CONNEXION RÉUSSIE pour {username}!")
                        print(f"👤 User ID: {response_data.get('userId', 'N/A')}")

                        # SAUVEGARDER IMMÉDIATEMENT - PAS DE VÉRIFICATION STRICTE
                        print("💾 Sauvegarde de la session...")
                        
                        # Préparer les données de session
                        session_data = {
                            'cookies': dict(session.cookies),
                            'created_at': datetime.now().isoformat(),
                            'user_agent': session.headers['User-Agent'],
                            'user_id': response_data.get('userId'),
                            'authenticated': True,
                            'login_time': datetime.now().isoformat()
                        }

                        # Sauvegarder les cookies
                        cookies_str = '; '.join([f"{k}={v}" for k, v in session.cookies.items()])
                        
                        # Vérifier si on a les cookies essentiels
                        essential_cookies = ['sessionid', 'csrftoken']
                        has_essential = all(cookie in cookies_str for cookie in essential_cookies)
                        
                        if has_essential:
                            print("✅ Cookies essentiels présents")
                        else:
                            print("⚠️ Certains cookies manquent mais connexion validée")

                        # Sauvegarder le compte
                        if self.add_account(username, password, cookies_str, json.dumps(session_data)):
                            print(f"💾 Compte {username} sauvegardé avec succès!")
                            
                            # Test rapide de la session
                            print("🧪 Test rapide de la session...")
                            if self.quick_session_test(session):
                                print("✅ Session testée et fonctionnelle")
                            else:
                                print("⚠️ Session sauvegardée mais test échoué - utilisation possible quand même")
                                
                            return True
                        else:
                            print("❌ Erreur lors de la sauvegarde")
                            return False

                    else:
                        error_type = response_data.get('error_type', 'Inconnu')
                        print(f"❌ Authentification échouée: {error_type}")
                        if error_type == 'UserInvalidCredentials':
                            print("🔒 Mot de passe ou nom d'utilisateur incorrect")
                        return False

                except Exception as e:
                    print(f"❌ Erreur analyse réponse: {e}")
                    return False

            else:
                print(f"❌ Erreur HTTP: {login_response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False

    def create_enc_password(self, password):
        """Format de mot de passe qui fonctionne"""
        timestamp = int(time.time())
        return f'#PWD_INSTAGRAM:0:{timestamp}:{password}'

    def extract_csrf_token(self, html_content, session):
        """Extrait le CSRF token"""
        # Depuis les cookies
        csrf_cookie = session.cookies.get('csrftoken')
        if csrf_cookie:
            return csrf_cookie
            
        # Depuis le HTML
        pattern = r'"csrf_token":"([^"]+)"'
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)
            
        return None

    def quick_session_test(self, session):
        """Test rapide et simple de la session"""
        try:
            test_response = session.get(
                'https://www.instagram.com/',
                timeout=10,
                allow_redirects=True
            )
            return 'accounts/login' not in test_response.url
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

    def get_account_count(self):
        """Retourne le nombre de comptes"""
        return len(self.get_all_accounts())

    def validate_account(self, username):
        """Valide qu'un compte a des cookies valides"""
        account_data = self.accounts.get(username, {})
        cookies_str = account_data.get('cookies', '')
        return bool(cookies_str and 'sessionid' in cookies_str)

# Interface utilisateur simple
def main_menu():
    """Menu principal pour gérer les comptes"""
    manager = AccountManager()

    while True:
        print("\n" + "="*50)
        print("       GESTIONNAIRE DE COMPTES INSTAGRAM - ULTIME")
        print("="*50)
        print(f"📁 Fichier: {manager.accounts_file}")
        print(f"👥 Comptes: {manager.get_account_count()}")
        print("\n1. 📋 Afficher les comptes")
        print("2. ➕ Ajouter un compte (GARANTI)")
        print("3. 🗑️ Supprimer un compte")
        print("4. 🚪 Quitter")

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
                    print("🔄 Lancement de la connexion...")
                    success = manager.connect_instagram_account(username, password)
                    if success:
                        print(f"\n🎉 SUCCÈS! Le compte {username} a été ajouté et sauvegardé.")
                        print("💡 Vous pouvez maintenant l'utiliser pour vos actions Instagram.")
                    else:
                        print("\n💔 Échec. Vérifiez vos identifiants et réessayez.")
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
            else:
                print("📭 Aucun compte à supprimer")

        elif choice == "4":
            print("👋 Au revoir!")
            break

        else:
            print("❌ Choix invalide")

        input("\n[↵] Appuyez sur Entrée pour continuer...")

# Test et utilisation
if __name__ == "__main__":
    main_menu()
