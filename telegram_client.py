# telegram_client.py - MÊME FONCTIONNEMENT QU'AVANT + RÉPARATION COOKIES
import asyncio
import random
import time
import re
from datetime import datetime
from telethon import TelegramClient, events
from config import TELEGRAM_CONFIG
from account_manager import AccountManager
from instagram_tasks import execute_instagram_task

class SmmKingdomAutomation:
    def __init__(self):
        self.api_id = TELEGRAM_CONFIG["api_id"]
        self.api_hash = TELEGRAM_CONFIG["api_hash"]
        self.session_name = TELEGRAM_CONFIG["session_name"]
        self.bot_username = TELEGRAM_CONFIG["bot_username"]
        self.account_manager = AccountManager()
        self.completed_tasks = 0
        self.is_running = True

        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash
        )

    def log_time(self):
        """Retourne le timestamp formaté"""
        return datetime.now().strftime("%H:%M:%S")

    def log(self, message):
        """Affiche les logs en temps réel"""
        timestamp = self.log_time()
        print(f"{timestamp} {message}")

    async def start(self):
        """Démarre l'automatisation"""
        try:
            self.log("[🔗] Connexion à Telegram...")
            await self.client.start()

            me = await self.client.get_me()
            self.log(f"[✅] Connecté en tant que: {me.username}")

            # DÉMARRER L'AUTOMATISATION DIRECTE COMME AVANT
            await self.automation_loop()

        except Exception as e:
            self.log(f"[❌] Erreur: {e}")
        finally:
            await self.cleanup()

    async def automation_loop(self):
        """Boucle d'automatisation des tâches - MÊME QU'AVANT"""
        self.log("[⚡] Démarrage automation SMM Kingdom Task")

        cycle = 0
        while self.is_running:
            cycle += 1
            self.log(f"[🔄] Cycle {cycle}")

            try:
                # MÊME NAVIGATION QU'AVANT
                await self.client.send_message(self.bot_username, '/start')
                await asyncio.sleep(2)

                await self.client.send_message(self.bot_username, 'Tasks')
                await asyncio.sleep(2)

                await self.client.send_message(self.bot_username, 'Instagram')
                await asyncio.sleep(2)

                # MÊME TRAITEMENT DES COMPTES QU'AVANT
                task_done = await self.process_all_accounts()

                if task_done:
                    self.log("[✅] Tâche terminée")
                else:
                    self.log("[ℹ️] Aucune tâche disponible")

                # MÊME PAUSE QU'AVANT
                await asyncio.sleep(15)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"[⚠️] Erreur: {e}")
                await asyncio.sleep(10)

    async def process_all_accounts(self):
        """Traite tous les comptes - MÊME QU'AVANT MAIS AVEC RÉPARATION"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.log("[❌] Aucun compte Instagram disponible")
            return False

        self.log(f"[🔍] Recherche de tâches avec {len(accounts)} compte(s)")

        for username, cookies_str in accounts:
            if not self.is_running:
                break

            self.log(f"Username: {username}")

            # SÉLECTION DU COMPTE COMME AVANT
            await self.client.send_message(self.bot_username, username)
            await asyncio.sleep(3)

            # VÉRIFICATION TÂCHE COMME AVANT
            task_text = await self.get_last_message()

            if task_text and self.is_task_available(task_text):
                # AFFICHAGE TÂCHE COMME AVANT
                task_info = self.analyze_task(task_text)
                if task_info:
                    self.log(f"[🔍] :{task_info['link']} |{task_info['type']}")
                    if task_info.get('user_id'):
                        self.log(f"[🔍] USER ID : {task_info['user_id']}")

                # EXÉCUTION AVEC RÉPARATION AUTO SI BESOIN
                self.log(f"[🎯] Exécution de la tâche avec le compte: {username}")

                # ESSAYER D'EXÉCUTER LA TÂCHE
                success = execute_instagram_task(task_text, cookies_str, username)

                if success:
                    # SUCCÈS - MÊME COMPORTEMENT QU'AVANT
                    await self.client.send_message(self.bot_username, 'Completed')
                    await asyncio.sleep(2)

                    self.completed_tasks += 1
                    self.log("[+] Tâche réussie")

                    await asyncio.sleep(2)
                    return True
                else:
                    # ÉCHEC - TENTER LA RÉPARATION AUTOMATIQUE
                    self.log("[-] Échec de l'exécution - Tentative de réparation...")

                    if await self.try_auto_repair(username):
                        self.log("[🔄] Réparation réussie - Nouvelle tentative...")
                        # Réessayer avec les nouveaux cookies
                        new_accounts = self.account_manager.get_all_accounts()
                        for new_user, new_cookies in new_accounts:
                            if new_user == username:
                                success_retry = execute_instagram_task(task_text, new_cookies, username)
                                if success_retry:
                                    await self.client.send_message(self.bot_username, 'Completed')
                                    await asyncio.sleep(2)
                                    self.completed_tasks += 1
                                    self.log("[+] Tâche réussie après réparation")
                                    return True

                    self.log("[-] Échec même après réparation")

            # RETOUR AU MENU COMME AVANT
            await self.client.send_message(self.bot_username, 'Back')
            await asyncio.sleep(1)
            await self.client.send_message(self.bot_username, 'Instagram')
            await asyncio.sleep(2)

        return False

    async def try_auto_repair(self, username):
        """Tente de réparer automatiquement un compte en échec"""
        try:
            self.log(f"[🔧] Réparation automatique de {username}...")

            # Récupérer le mot de passe sauvegardé
            password = self.account_manager.get_password(username)
            if not password:
                self.log(f"[❌] {username} - Pas de mot de passe sauvegardé")
                return False

            # Réparer le compte
            success = self.account_manager.connect_instagram_account(username, password)
            if success:
                self.log(f"[✅] {username} - Réparé avec succès!")
                return True
            else:
                self.log(f"[❌] {username} - Échec réparation")
                return False

        except Exception as e:
            self.log(f"[💥] Erreur réparation: {e}")
            return False

    def analyze_task(self, text):
        """Analyse la tâche - MÊME QU'AVANT"""
        if not text:
            return None

        task_info = {
            'type': 'Action',
            'link': '',
            'user_id': ''
        }

        if 'follow' in text.lower():
            task_info['type'] = 'Follow the profile'
        elif 'like' in text.lower():
            task_info['type'] = 'Like the post'
        elif 'comment' in text.lower():
            task_info['type'] = 'Comment on post'
        elif 'story' in text.lower():
            task_info['type'] = 'Watch story'
        elif 'video' in text.lower() or 'watch' in text.lower():
            task_info['type'] = 'Watch video'

        links = re.findall(r'https?://(?:www\.)?instagram\.com/[^\s]+', text)
        if links:
            task_info['link'] = links[0]

        user_ids = re.findall(r'user[_\s]?id:?\s*(\d+)', text, re.IGNORECASE)
        if user_ids:
            task_info['user_id'] = user_ids[0]

        return task_info if task_info['link'] else None

    async def get_last_message(self):
        """Récupère le dernier message - MÊME QU'AVANT"""
        try:
            async for message in self.client.iter_messages(self.bot_username, limit=1):
                return message.text
        except:
            return None

    def is_task_available(self, text):
        """Vérifie si une tâche est disponible - MÊME QU'AVANT"""
        if not text:
            return False

        ignore = [
            'no active task', 'choose account', 'select account',
            'instagram accounts', 'choose social network',
            'please give us your profile', 'username for tasks',
            'sorry, but there are no active tasks'
        ]
        if any(pattern in text.lower() for pattern in ignore):
            return False

        tasks = [
            'instagram.com', 'like the post', 'follow the profile',
            'comment on post', 'watch the story', 'open the video',
            'action:', 'reward:'
        ]
        return any(pattern in text.lower() for pattern in tasks)

    async def cleanup(self):
        """Nettoyage - MÊME QU'AVANT"""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
        except:
            pass

# LANCEUR - MÊME QU'AVANT
async def run_smm_automation():
    bot = SmmKingdomAutomation()
    await bot.start()

def start_smm_automation():
    """Lance l'automatisation - MÊME QU'AVANT"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_smm_automation())
    except KeyboardInterrupt:
        print(f"\n[👋] Arrêté")
    except Exception as e:
        print(f"[❌] Erreur: {e}")

if __name__ == "__main__":
    start_smm_automation()
