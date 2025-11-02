# account_manager.py - VERSION COMPLÈTE CORRIGÉE AVEC INSTAGRAPI
import json
import os
import time
import random
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired

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

    def connect_instagram_account(self, username, password):
        """
        Connexion Instagram avec Instagrapi - VERSION CORRIGÉE
        """
        print(f"🔐 Connexion Instagram pour {username}...")

        # Sauvegarder d'abord le compte avec le mot de passe
        self.add_account(username, password, "", "")

        try:
            # Créer le client Instagrapi
            client = Client()
            
            # Configurer pour éviter la détection
            client.delay_range = [2, 5]
            client.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
            
            print("📡 Tentative de connexion avec Instagrapi...")
            
            # Essayer de se connecter
            client.login(username, password)
            
            # Vérifier si la connexion a réussi
            user_id = client.user_id
            if user_id:
                print(f"✅ Connexion réussie pour {username}")
                print(f"👤 User ID: {user_id}")
                
                # Sauvegarder la session
                self._save_instagrapi_session(client, username)
                return True
            else:
                print("❌ Connexion échouée - Aucun user_id reçu")
                return False

        except TwoFactorRequired:
            print("🔐 Authentification à deux facteurs requise")
            print("💡 Désactivez 2FA temporairement ou utilisez l'app officielle")
            return False
            
        except ChallengeRequired:
            print("🚫 Défi de sécurité Instagram requis")
            print("💡 Connectez-vous manuellement d'abord depuis l'app officielle")
            return self._handle_challenge_retry(username, password)
            
        except LoginRequired:
            print("❌ Connexion requise - Identifiants incorrects ou compte bloqué")
            return False
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {str(e)}")
            return False

    def _handle_challenge_retry(self, username, password):
        """Tentative de reconnexion après un défi de sécurité"""
        print("🔄 Tentative de reconnexion dans 10 secondes...")
        time.sleep(10)
        
        try:
            client = Client()
            client.delay_range = [3, 7]
            
            # Réessayer avec des paramètres différents
            client.login(username, password)
            
            if client.user_id:
                print(f"✅ Connexion réussie après défi de sécurité!")
                self._save_instagrapi_session(client, username)
                return True
        except Exception as e:
            print(f"❌ Échec de la reconnexion: {str(e)}")
            
        return False

    def _save_instagrapi_session(self, client, username):
        """Sauvegarde la session Instagrapi"""
        try:
            # Récupérer les données de session
            session_data = client.get_settings()
            cookies = client.get_cookies()
            
            # Convertir les cookies en string pour compatibilité
            cookies_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            
            # Préparer les données de session complètes
            session_info = {
                'settings': session_data,
                'cookies': cookies,
                'user_id': client.user_id,
                'created_at': datetime.now().isoformat(),
                'user_agent': client.get_user_agent()
            }
            
            # Mettre à jour le compte
            self.update_cookies(username, cookies_str)
            self.update_session(username, json.dumps(session_info))
            
            print(f"💾 Session sauvegardée pour {username}")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde de session: {e}")

    def test_account_session(self, username):
        """
        Teste si une session est encore valide
        """
        account_data = self.accounts.get(username, {})
        session_data_str = account_data.get('session_data', '')
        
        if not session_data_str:
            print(f"❌ Aucune session pour {username}")
            return False
            
        try:
            session_data = json.loads(session_data_str)
            settings = session_data.get('settings', {})
            
            client = Client(settings=settings)
            
            # Tester la session en récupérant les infos du compte
            user_info = client.account_info()
            if user_info:
                print(f"✅ Session valide pour {username}")
                return True
                
        except LoginRequired:
            print(f"❌ Session expirée pour {username}")
            return False
        except Exception as e:
            print(f"⚠️  Erreur test session {username}: {str(e)}")
            return False
            
        return False

    def reconnect_account(self, username):
        """
        Reconnexion automatique d'un compte
        """
        account_data = self.accounts.get(username, {})
        password = account_data.get('password', '')
        
        if not password:
            print(f"❌ Mot de passe manquant pour {username}")
            return False
            
        print(f"🔄 Reconnexion du compte {username}...")
        return self.connect_instagram_account(username, password)

    def get_client_for_account(self, username):
        """
        Retourne un client Instagrapi configuré pour un compte
        """
        account_data = self.accounts.get(username, {})
        session_data_str = account_data.get('session_data', '')
        
        if not session_data_str:
            print(f"❌ Aucune session pour {username}")
            return None
            
        try:
            session_data = json.loads(session_data_str)
            settings = session_data.get('settings', {})
            
            client = Client(settings=settings)
            client.delay_range = [1, 3]
            
            # Tester la session avec une requête simple
            client.get_timeline_feed()
            return client
            
        except LoginRequired:
            print(f"🔁 Session expirée pour {username}, tentative de reconnexion...")
            if self.reconnect_account(username):
                return self.get_client_for_account(username)
            return None
        except Exception as e:
            print(f"❌ Erreur client pour {username}: {str(e)}")
            return None

    def get_all_valid_clients(self):
        """
        Retourne tous les clients valides pour l'automatisation
        """
        valid_clients = {}
        accounts = self.get_all_accounts()
        
        for username, cookies, session_data in accounts:
            client = self.get_client_for_account(username)
            if client:
                valid_clients[username] = client
                print(f"✅ {username} - Client prêt")
            else:
                print(f"❌ {username} - Client non disponible")
                
        return valid_clients

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

    def check_all_sessions(self):
        """Vérifie l'état de toutes les sessions"""
        print("🔍 Vérification de toutes les sessions...")
        accounts = self.get_all_accounts()
        valid_count = 0
        
        for username, cookies, session_data in accounts:
            if self.test_account_session(username):
                valid_count += 1
                
        print(f"📊 Sessions valides: {valid_count}/{len(accounts)}")
        return valid_count

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
        print("2. ➕ Ajouter un compte (Instagrapi)")
        print("3. 🔄 Tester les sessions")
        print("4. 🗑️ Supprimer un compte")
        print("5. 🔄 Migrer depuis ancien format")
        print("6. 🚪 Quitter")

        choice = input("\n📝 Choix: ").strip()

        if choice == "1":
            manager.display_accounts()

        elif choice == "2":
            print("\n👤 AJOUTER UN COMPTE INSTAGRAM")
            username = input("[?] Nom d'utilisateur Instagram: ").strip()
            
            # Afficher le mot de passe en clair
            print("[🔓] Mot de passe Instagram: ", end="", flush=True)
            password = input()
            
            if username and password:
                print(f"\n[ℹ️] Résumé du compte:")
                print(f"   Utilisateur: {username}")
                print(f"   Mot de passe: {password}")

                confirm = input("[?] Confirmer l'ajout? (o/n): ").strip().lower()
                if confirm == 'o':
                    success = manager.connect_instagram_account(username, password)
                    
                    if success:
                        print("🎉 Compte ajouté avec succès!")
                    else:
                        print("💔 Échec de l'ajout du compte")
                        print("💡 Conseils:")
                        print("   - Vérifiez nom d'utilisateur/mot de passe")
                        print("   - Désactivez 2FA temporairement")
                        print("   - Connectez-vous manuellement d'abord sur l'app")
                else:
                    print("❌ Ajout annulé")
            else:
                print("❌ Nom d'utilisateur et mot de passe requis")

        elif choice == "3":
            print("\n🔍 TEST DES SESSIONS")
            manager.check_all_sessions()

        elif choice == "4":
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

        elif choice == "5":
            old_file = input("[?] Chemin de l'ancien fichier: ").strip()
            if old_file:
                migrate_from_old_format(manager, old_file)
            else:
                print("❌ Chemin invalide")

        elif choice == "6":
            print("👋 Au revoir!")
            break

        else:
            print("❌ Choix invalide")

        input("\n[↵] Appuyez sur Entrée pour continuer...")

# Test et utilisation
if __name__ == "__main__":
    main_menu()
