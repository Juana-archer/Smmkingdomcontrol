# telegram_client.py - SYNCHRONISATION COMPLÈTE
import asyncio
import random
import time
import re
from telethon import TelegramClient, events
from config import TELEGRAM_CONFIG, COLORS
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

    async def start(self):
        """Démarre l'automatisation avec synchronisation"""
        try:
            print(f"{COLORS['C']}[🔗] Connexion à Telegram...{COLORS['S']}")
            await self.client.start()

            me = await self.client.get_me()
            print(f"{COLORS['V']}[✅] Connecté en tant que: {me.username}{COLORS['S']}")

            # DÉMARRER AVEC SYNCHRONISATION
            await self.sync_and_automate()

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur: {e}{COLORS['S']}")
        finally:
            await self.cleanup()

    async def sync_and_automate(self):
        """Synchronise puis automatise"""
        # ÉTAPE 1: Synchroniser les comptes
        await self.sync_accounts()

        # ÉTAPE 2: Boucle d'automatisation
        await self.automation_loop()

    async def sync_accounts(self):
        """Synchronise les comptes entre le script et le bot"""
        print(f"{COLORS['C']}[🔄] SYNCHRONISATION DES COMPTES{COLORS['S']}")

        # Récupérer nos comptes
        our_accounts = self.account_manager.get_all_accounts()
        our_usernames = [acc[0] for acc in our_accounts]
        print(f"{COLORS['V']}[📊] {len(our_usernames)} compte(s) dans le script{COLORS['S']}")

        # Envoyer /start
        await self.client.send_message(self.bot_username, '/start')
        await asyncio.sleep(2)

        # Aller dans Manage accounts
        await self.client.send_message(self.bot_username, 'Manage accounts')
        await asyncio.sleep(2)

        # Aller dans Instagram accounts
        await self.client.send_message(self.bot_username, 'Instagram')
        await asyncio.sleep(3)

        # Récupérer les comptes du bot
        bot_accounts = await self.get_bot_accounts()
        print(f"{COLORS['V']}[📋] {len(bot_accounts)} compte(s) dans le bot{COLORS['S']}")

        # Ajouter nos comptes manquants au bot
        added_count = 0
        for username in our_usernames:
            if username not in bot_accounts:
                print(f"{COLORS['C']}[➕] Ajout de {username} au bot...{COLORS['S']}")
                if await self.add_account_to_bot(username):
                    added_count += 1
                await asyncio.sleep(2)

        if added_count > 0:
            print(f"{COLORS['V']}[✅] {added_count} compte(s) ajouté(s) au bot{COLORS['S']}")

        print(f"{COLORS['V']}[✅] Synchronisation terminée!{COLORS['S']}")

    async def get_bot_accounts(self):
        """Récupère les comptes depuis le bot"""
        try:
            # Lire les derniers messages pour trouver la liste des comptes
            accounts = []
            async for message in self.client.iter_messages(self.bot_username, limit=10):
                if message.text:
                    # Chercher les usernames dans le texte
                    usernames = re.findall(r'@?([a-zA-Z0-9_.]+)', message.text)
                    for user in usernames:
                        if len(user) > 3 and user not in ['instagram', 'com', 'http', 'https']:
                            accounts.append(user.lower())

            return list(set(accounts))  # Supprimer les doublons

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur lecture comptes bot: {e}{COLORS['S']}")
            return []

    async def add_account_to_bot(self, username):
        """Ajoute un compte au bot"""
        try:
            # Envoyer le username au bot
            await self.client.send_message(self.bot_username, username)
            await asyncio.sleep(2)

            # Vérifier si le bot demande des cookies
            async for message in self.client.iter_messages(self.bot_username, limit=3):
                if 'cookie' in message.text.lower() or 'session' in message.text.lower():
                    # Répondre que les cookies sont gérés automatiquement
                    await self.client.send_message(self.bot_username, 'auto')
                    await asyncio.sleep(2)
                    break

            return True

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur ajout {username}: {e}{COLORS['S']}")
            return False

    async def automation_loop(self):
        """Boucle d'automatisation des tâches"""
        print(f"{COLORS['C']}[⚡] DÉMARRAGE AUTOMATISATION{COLORS['S']}")

        cycle = 0
        while self.is_running:
            cycle += 1
            print(f"{COLORS['C']}[🔄] Cycle {cycle}{COLORS['S']}")

            try:
                # Aller dans Tasks
                await self.client.send_message(self.bot_username, 'Tasks')
                await asyncio.sleep(2)

                # Sélectionner Instagram
                await self.client.send_message(self.bot_username, 'Instagram')
                await asyncio.sleep(2)

                # Essayer chaque compte pour les tâches
                task_done = await self.process_all_accounts()

                if task_done:
                    print(f"{COLORS['V']}[✅] Tâche terminée{COLORS['S']}")
                else:
                    print(f"{COLORS['J']}[ℹ️] Aucune tâche{COLORS['S']}")

                # Pause entre les cycles
                await asyncio.sleep(15)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{COLORS['R']}[⚠️] Erreur: {e}{COLORS['S']}")
                await asyncio.sleep(10)

    async def process_all_accounts(self):
        """Traite tous les comptes pour trouver des tâches"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            print(f"{COLORS['R']}[❌] Aucun compte{COLORS['S']}")
            return False

        print(f"{COLORS['C']}[🔍] Recherche avec {len(accounts)} compte(s){COLORS['S']}")

        for username, cookies_str in accounts:
            print(f"{COLORS['C']}[👤] Test: {username}{COLORS['S']}")

            # Sélectionner le compte dans le bot
            await self.client.send_message(self.bot_username, username)
            await asyncio.sleep(3)

            # Vérifier si une tâche est disponible
            task_text = await self.get_last_message()

            if task_text and self.is_task_available(task_text):
                print(f"{COLORS['V']}[🎯] Tâche trouvée!{COLORS['S']}")

                # Exécuter la tâche
                success = execute_instagram_task(task_text, cookies_str, username)

                if success:
                    # Marquer comme complété
                    await self.client.send_message(self.bot_username, 'Completed')
                    await asyncio.sleep(2)

                    self.completed_tasks += 1
                    print(f"{COLORS['V']}[💰] Tâche #{self.completed_tasks} terminée!{COLORS['S']}")
                    return True
                else:
                    print(f"{COLORS['R']}[💔] Échec exécution{COLORS['S']}")

            else:
                print(f"{COLORS['J']}[➖] Pas de tâche{COLORS['S']}")

            # Retour au menu des comptes
            await self.client.send_message(self.bot_username, 'Instagram')
            await asyncio.sleep(2)

        return False

    async def get_last_message(self):
        """Récupère le dernier message du bot"""
        try:
            async for message in self.client.iter_messages(self.bot_username, limit=1):
                return message.text
        except:
            return None

    def is_task_available(self, text):
        """Vérifie si une tâche est disponible"""
        if not text:
            return False

        # Ignorer ces messages
        ignore = ['no active task', 'choose account', 'select account', 'instagram accounts']
        if any(pattern in text.lower() for pattern in ignore):
            return False

        # Tâches valides
        tasks = ['instagram.com', 'like the post', 'follow the profile', 'action:', 'reward:']
        return any(pattern in text.lower() for pattern in tasks)

    async def cleanup(self):
        """Nettoyage"""
        try:
            if self.client and self.client.is_connected():
                await self.client.disconnect()
        except:
            pass

# Lanceur
async def run_sync_automation():
    bot = SmmKingdomAutomation()
    await bot.start()

def start_smm_automation():
    """Lance l'automatisation synchronisée"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_sync_automation())
    except KeyboardInterrupt:
        print(f"\n{COLORS['J']}[👋] Arrêté{COLORS['S']}")
    except Exception as e:
        print(f"{COLORS['R']}[❌] Erreur: {e}{COLORS['S']}")

if __name__ == "__main__":
    start_smm_automation()
