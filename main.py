#!/usr/bin/env python3
# main.py - Script principal
import asyncio
import json
from config import COLORS
from control_system import ControlSystem
from account_manager import AccountManager
from telegram_client import TelegramBot
from ui import Interface

class SmmKingdomApp:
    def __init__(self):
        self.interface = Interface()
        self.control = ControlSystem()
        self.account_manager = AccountManager()
        self.running = True

    def verify_license(self):
        """Vérifie la licence avec système d'abonnement"""
        self.interface.clear_screen()
        self.interface.show_message("🔐 VÉRIFICATION ABONNEMENT...", "info")

        # Première configuration
        self.control.first_time_setup()

        # Vérification licence
        valid, message = self.control.check_license()

        if not valid:
            self.interface.show_message(f"❌ {message}", "error")
            self.interface.show_message("📞 Contactez Dah Ery pour renouveler", "warning")

            # Affiche les infos de contact
            try:
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
                    print(f"{COLORS['J']}[👤] Votre ID: {user_data['user_id']}{COLORS['S']}")
            except:
                pass

            self.interface.press_enter()
            return False

        self.interface.show_message(f"✅ {message}", "success")
        self.interface.show_message("👑 Contrôlé par Dah Ery", "info")
        self.interface.press_enter()
        return True

    def main_menu(self):
        """Boucle principale du menu"""
        while self.running:
            self.interface.clear_screen()
            self.interface.display_menu()

            choice = self.interface.get_choice()

            if choice == "1":
                self.start_bot()
            elif choice == "2":
                self.add_account()
            elif choice == "3":
                self.view_accounts()
            elif choice == "4":
                self.delete_account()
            elif choice == "5":
                self.view_cookies()
            elif choice == "0":
                self.quit_app()
            else:
                self.interface.show_message("❌ Choix invalide", "error")
                self.interface.press_enter()

    def start_bot(self):
        """Démarre le bot Telegram"""
        self.interface.clear_screen()
        self.interface.show_message("🤖 DÉMARRAGE DU BOT", "info")

        try:
            bot = TelegramBot()
            asyncio.run(bot.start())
        except Exception as e:
            self.interface.show_message(f"❌ Erreur: {e}", "error")
            self.interface.press_enter()

    def add_account(self):
        """Ajoute un compte Instagram"""
        self.interface.clear_screen()
        self.interface.show_message("👤 AJOUTER UN COMPTE", "info")

        username = self.interface.get_choice("Nom d'utilisateur Instagram")
        password = self.interface.get_choice("Mot de passe Instagram")

        if username and password:
            self.account_manager.connect_instagram_account(username, password)
        else:
            self.interface.show_message("❌ Champs vides", "error")

        self.interface.press_enter()

    def view_accounts(self):
        """Affiche les comptes"""
        self.interface.clear_screen()
        self.interface.show_message("📂 MES COMPTES", "info")

        self.account_manager.display_accounts()
        self.interface.press_enter()

    def delete_account(self):
        """Supprime un compte"""
        self.interface.clear_screen()
        self.interface.show_message("🗑️ SUPPRIMER UN COMPTE", "warning")

        if not self.account_manager.display_accounts():
            self.interface.press_enter()
            return

        choice = self.interface.get_choice("Numéro à supprimer (0 pour annuler)")

        if choice.isdigit():
            index = int(choice) - 1
            if index >= 0:
                self.account_manager.delete_account(index)

        self.interface.press_enter()

    def view_cookies(self):
        """Affiche les cookies"""
        self.interface.clear_screen()
        self.interface.show_message("🍪 COOKIES DES COMPTES", "info")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("Aucun compte", "warning")
        else:
            for i, acc in enumerate(accounts, 1):
                user, cookies = acc.split('|', 1)
                print(f"{COLORS['o']}[{i}] {user}{COLORS['S']}")
                print(f"   {cookies[:50]}...")
                print()

        self.interface.press_enter()

    def quit_app(self):
        """Quitte l'application"""
        self.interface.clear_screen()
        self.interface.show_message("👋 Au revoir!", "info")
        self.interface.show_message("📞 Développé par Dah Ery", "info")
        self.running = False

def main():
    app = SmmKingdomApp()

    # Vérification de licence
    if not app.verify_license():
        return

    # Lancement
    app.main_menu()

if __name__ == "__main__":
    main()
