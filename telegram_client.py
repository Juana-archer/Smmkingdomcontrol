# telegram_client.py - VERSION SIMPLIFIÉE
import asyncio
import re
from telethon import TelegramClient, events
from config import TELEGRAM_CONFIG, COLORS

class TelegramBot:
    def __init__(self):
        self.client = TelegramClient(
            TELEGRAM_CONFIG["session_name"],
            TELEGRAM_CONFIG["api_id"],
            TELEGRAM_CONFIG["api_hash"]
        )
        self.setup_handlers()

    def setup_handlers(self):
        """Configure les handlers"""

        @self.client.on(events.NewMessage(from_users=TELEGRAM_CONFIG["bot_username"]))
        async def handler(event):
            await self.handle_message(event)

    async def handle_message(self, event):
        """Gère les messages du bot"""
        message = event.message.message

        # Tâche Instagram détectée
        if "instagram.com" in message and ("like" in message.lower() or "follow" in message.lower() or "comment" in message.lower()):
            print(f"{COLORS['V']}[🎯] Tâche détectée{COLORS['S']}")

            try:
                from account_manager import AccountManager
                from instagram_tasks import InstagramAutomation

                account_manager = AccountManager()
                accounts = account_manager.get_all_accounts()

                if accounts:
                    username, cookies = accounts[0].split('|', 1)

                    # Exécute la tâche
                    instagram_bot = InstagramAutomation()
                    success = instagram_bot.execute_task(message, cookies, username)

                    if success:
                        await event.reply("✅Completed")
                        print(f"{COLORS['V']}[✅] Tâche complétée{COLORS['S']}")
                    else:
                        print(f"{COLORS['R']}[❌] Échec tâche{COLORS['S']}")
                else:
                    print(f"{COLORS['R']}[⚠️] Aucun compte{COLORS['S']}")

            except Exception as e:
                print(f"{COLORS['R']}[💥] Erreur: {e}{COLORS['S']}")

    async def send_accounts_loop(self):
        """Envoie les comptes en boucle simple"""
        from account_manager import AccountManager

        account_manager = AccountManager()
        accounts = account_manager.get_all_accounts()

        if not accounts:
            print(f"{COLORS['R']}[⚠️] Aucun compte Instagram{COLORS['S']}")
            return

        print(f"{COLORS['C']}[🔄] Envoi des comptes...{COLORS['S']}")

        index = 0
        while True:
            username = accounts[index].split('|')[0]

            # Envoie le compte
            await self.client.send_message("@SmmKingdomTasksBot", username)
            await asyncio.sleep(15)  # Attend 15 secondes

            # Passe au compte suivant
            index = (index + 1) % len(accounts)

    async def start(self):
        """Démarre le bot"""
        try:
            phone = input(f"{COLORS['o']}[?] Votre numéro Telegram: {COLORS['B']}")

            await self.client.start(phone=phone)
            print(f"{COLORS['V']}[📡] Bot démarré{COLORS['S']}")

            # Démarre l'envoi des comptes
            await self.send_accounts_loop()

            await self.client.run_until_disconnected()
        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur: {e}{COLORS['S']}")
