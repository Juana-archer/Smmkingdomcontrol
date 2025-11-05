# telegram_client.py - VERSION COMPATIBLE CORRIGÉE
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

    def print_username(self, username):
        """Affiche le username avec timestamp"""
        timestamp = self.log_time()
        print(f"{timestamp} username :{username}")

    async def start(self):
        """Démarre l'automatisation"""
        try:
            self.log("[🔗] Connexion à Telegram...")
            await self.client.start()

            me = await self.client.get_me()
            self.log(f"[✅] Connecté en tant que: {me.username if me else 'None'}")

            # DÉMARRER L'AUTOMATISATION
            await self.automation_loop()

        except Exception as e:
            self.log(f"[❌] Erreur: {e}")
        finally:
            await self.cleanup()

    async def automation_loop(self):
        """Boucle d'automatisation des tâches - CONTINUITÉ DES CYCLES"""
        self.log("[⚡] Démarrage automation SMM Kingdom Task")

        cycle = 0

        # PREMIER DÉMARRAGE SEULEMENT : /start et Tasks
        await self.client.send_message(self.bot_username, '/start')
        await asyncio.sleep(2)
        await self.client.send_message(self.bot_username, 'Tasks')
        await asyncio.sleep(2)

        while self.is_running:
            cycle += 1
            self.log(f"[🔄] Cycle {cycle}")

            try:
                # TOUJOURS COMMENCER PAR "Instagram" (pas de /start après le premier cycle)
                await self.client.send_message(self.bot_username, 'Instagram')
                await asyncio.sleep(2)

                # Traiter chaque compte pour les tâches
                await self.process_all_accounts()

                # Pause entre les cycles
                await asyncio.sleep(15)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"[⚠️] Erreur: {e}")
                await asyncio.sleep(10)

    async def process_all_accounts(self):
        """Traite tous les comptes pour trouver et exécuter des tâches - TOUTES LES ACTIONS"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.log("[❌] Aucun compte Instagram disponible")
            return

        for username, cookies, session_data in accounts:
            if not self.is_running:
                break

            # Afficher le username AVEC TIMESTAMP
            self.print_username(username)

            # Sélectionner le compte dans le bot SMM Kingdom
            await self.client.send_message(self.bot_username, username)
            await asyncio.sleep(3)

            # BOUCLE POUR TRAITER TOUTES LES TÂCHES DU COMPTE COURANT
            task_executed = False
            while self.is_running:
                task_text = await self.get_last_message()

                # VÉRIFIER SI "NO ACTIVE TASKS" - alors cliquer "Instagram" pour compte suivant
                if task_text and self.has_no_tasks(task_text):
                    await self.client.send_message(self.bot_username, 'Instagram')
                    await asyncio.sleep(2)
                    break

                # VÉRIFIER SI ON EST DANS "PLEASE GIVE USERNAME" - alors sortir pour compte suivant
                if task_text and self.is_username_request(task_text):
                    break

                # VÉRIFIER SI TÂCHE DISPONIBLE (TOUTES LES ACTIONS)
                if task_text and self.is_real_task_all_actions(task_text):
                    # Analyser la tâche détectée
                    task_info = self.analyze_real_task_all_actions(task_text)
                    if task_info and task_info['link']:
                        # AFFICHER LE LIEN ET L'ACTION
                        timestamp = self.log_time()
                        print(f"{timestamp} 🔗 {task_info['link']}")
                        print(f"{timestamp} 🎯 Action: {task_info['action']}")

                        # CORRECTION : Appel compatible avec 2 paramètres
                        success = execute_instagram_task(task_text, username)

                        if success:
                            # Marquer comme complété dans SMM Kingdom
                            await self.client.send_message(self.bot_username, 'Completed')
                            await asyncio.sleep(3)

                            self.completed_tasks += 1
                            timestamp = self.log_time()
                            print(f"{timestamp} ✅ Tâche exécutée avec succès")
                            task_executed = True

                            # ATTENDRE POUR VOIR SI UNE AUTRE TÂCHE APPARAÎT
                            await asyncio.sleep(5)

                            # VÉRIFIER SI UNE NOUVELLE TÂCHE EST DISPONIBLE
                            new_task_text = await self.get_last_message()
                            if new_task_text and self.is_real_task_all_actions(new_task_text):
                                # CONTINUER AVEC LA PROCHAINE TÂCHE
                                continue
                            else:
                                # PAS D'AUTRE TÂCHE - CLIQUER "INSTAGRAM" POUR COMPTE SUIVANT
                                await self.client.send_message(self.bot_username, 'Instagram')
                                await asyncio.sleep(2)
                                break
                        else:
                            timestamp = self.log_time()
                            print(f"{timestamp} ❌ Échec execution")
                            # CORRECTION : Utiliser la fonction existante d'AccountManager
                            # self.account_manager.mark_problem_account(username) - FONCTION SUPPRIMÉE
                            break

                # Si aucune tâche détectée après un certain temps, passer au compte suivant
                if not task_executed:
                    await asyncio.sleep(3)
                    # Vérifier une dernière fois
                    final_check = await self.get_last_message()
                    if not (final_check and self.is_real_task_all_actions(final_check)):
                        await self.client.send_message(self.bot_username, 'Instagram')
                        await asyncio.sleep(2)
                        break
                else:
                    await asyncio.sleep(2)

    def is_real_task_all_actions(self, text):
        """Détection de TOUTES les actions SMM Kingdom"""
        if not text:
            return False

        text_lower = text.lower()

        # IGNORER ABSOLUMENT ces messages
        ignore_patterns = [
            'no active tasks',
            'sorry, but there are no active tasks',
            'please give us your profile',
            'username for tasks completing',
            'choose social network',
            'instagram accounts',
            'back to tasks',
            'remove_',
            'dahe.r',
            'daher_e',
            'juan.rved'
        ]

        if any(pattern in text_lower for pattern in ignore_patterns):
            return False

        # ÉLÉMENTS REQUIS POUR TOUTES LES TÂCHES
        required_patterns = [
            'link',
            'action',
            'instagram.com',
            'cashcoins'
        ]

        # ACTIONS SUPPORTÉES
        supported_actions = [
            'like the post',
            'follow the profile',
            'comment on post',
            'watch the story',
            'watch the video',
            'open the video'
        ]

        # VÉRIFIER LES ÉLÉMENTS REQUIS + AU MOINS 1 ACTION SUPPORTÉE
        has_required = all(pattern in text_lower for pattern in required_patterns)
        has_supported_action = any(action in text_lower for action in supported_actions)

        return has_required and has_supported_action

    def analyze_real_task_all_actions(self, text):
        """Analyse de TOUTES les actions SMM Kingdom"""
        if not text:
            return None

        task_info = {
            'type': 'Unknown',
            'link': '',
            'action': '',
            'reward': ''
        }

        # DÉTECTER LE TYPE D'ACTION
        text_lower = text.lower()
        action_patterns = {
            'like the post': 'Like the post',
            'follow the profile': 'Follow the profile',
            'comment on post': 'Comment on post',
            'watch the story': 'Watch the story',
            'watch the video': 'Watch the video',
            'open the video': 'Watch the video'
        }

        for pattern, action_name in action_patterns.items():
            if pattern in text_lower:
                task_info['action'] = action_name
                task_info['type'] = action_name
                break

        # EXTRAIRE TOUS LES TYPES DE LIENS INSTAGRAM
        link_patterns = [
            r'https?://(?:www\.)?instagram\.com/p/[^\s]+',  # posts
            r'https?://(?:www\.)?instagram\.com/reel/[^\s]+',  # reels
            r'https?://(?:www\.)?instagram\.com/stories/[^\s]+',  # stories
            r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+/?(?:\?[^\s]*)?',  # profils
            r'link\s*:\s*(https?://[^\s]+)'  # format "Link :"
        ]

        for pattern in link_patterns:
            links = re.findall(pattern, text, re.IGNORECASE)
            if links:
                task_info['link'] = links[0].strip()
                break

        # EXTRAIRE LA RÉCOMPENSE
        reward_match = re.search(r'reward\s*:\s*([0-9.]+)\s*cashcoins', text_lower)
        if reward_match:
            task_info['reward'] = f"{reward_match.group(1)} CashCoins"
        else:
            task_info['reward'] = 'CashCoins'

        return task_info if task_info['link'] else None

    def is_username_request(self, text):
        """Vérifie si le bot demande un username"""
        if not text:
            return False

        request_patterns = [
            'please give us your profile',
            'username for tasks completing',
            'give us your profile'
        ]

        text_lower = text.lower()
        return any(pattern in text_lower for pattern in request_patterns)

    def has_no_tasks(self, text):
        """Vérifie si le message indique qu'il n'y a pas de tâches"""
        if not text:
            return False

        no_task_patterns = [
            'no active tasks',
            'sorry, but there are no active tasks',
            'aucune tâche active',
            'no tasks available',
            'sorry, no tasks'
        ]

        text_lower = text.lower()
        return any(pattern in text_lower for pattern in no_task_patterns)

    async def get_last_message(self):
        """Récupère le dernier message du bot"""
        try:
            async for message in self.client.iter_messages(self.bot_username, limit=5):
                if message.text and not message.out:
                    return message.text.strip()
            return None
        except Exception:
            return None

    async def cleanup(self):
        """Nettoyage"""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
        except:
            pass

# Lanceur
async def run_smm_automation():
    bot = SmmKingdomAutomation()
    await bot.start()

def start_smm_automation():
    """Lance l'automatisation"""
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
