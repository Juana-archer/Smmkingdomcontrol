#!/usr/bin/env python3
# main.py - Script principal SmmKingdomTask
import asyncio
import json
import os
import sys
from config import COLORS
from control_system import ControlSystem
from account_manager import AccountManager
from telegram_client import start_smm_automation
from ui import Interface

class SmmKingdomApp:
    def __init__(self):
        self.interface = Interface()
        self.control = ControlSystem()
        self.account_manager = AccountManager()
        self.running = True

    def verify_license(self):
        """Vérifie la licence - BLOQUE si non activé"""
        self.interface.clear_screen()
        print(f"{COLORS['C']}[🔐] Vérification de votre licence...{COLORS['S']}")

        # Cette fonction BLOQUE le script si non activé
        valid, message = self.control.check_license()

        if valid:
            print(f"{COLORS['V']}[✅] {message}{COLORS['S']}")
            print(f"{COLORS['J']}[👑] Contrôlé par Dah Ery{COLORS['S']}")
            self.interface.press_enter()
            return True
        else:
            # Le script est déjà bloqué par check_license()
            # Cette partie ne sera jamais atteinte
            return False

    def show_welcome(self):
        """Affiche l'écran de bienvenue"""
        self.interface.clear_screen()
        
        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║           SMM KINGDOM TASK v3.0        ║{COLORS['S']}")
        print(f"{COLORS['C']}║         Système Automatique SMM        ║{COLORS['S']}")
        print(f"{COLORS['C']}║           Contrôlé par Dah Ery         ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ 📱 Gagnez de l'argent automatiquement  ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 🤖 Bot 24h/24 - Aucune intervention    ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💰 CashCoins directement sur Telegram   ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        
        input(f"{COLORS['J']}⏎ Appuyez sur Entrée pour continuer...{COLORS['S']}")

    def display_menu(self):
        """Affiche le menu principal"""
        self.interface.clear_screen()
        
        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║           SMM KINGDOM TASK v3.0        ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║  1. 🤖 Démarrer l'automatisation       ║{COLORS['S']}")
        print(f"{COLORS['B']}║  2. 👤 Ajouter un compte Instagram     ║{COLORS['S']}")
        print(f"{COLORS['B']}║  3. 📂 Voir mes comptes                ║{COLORS['S']}")
        print(f"{COLORS['B']}║  4. 🗑️  Supprimer un compte            ║{COLORS['S']}")
        print(f"{COLORS['B']}║  5. ℹ️  Instructions d'utilisation      ║{COLORS['S']}")
        print(f"{COLORS['B']}║  0. 🚪 Quitter                         ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()

    def show_instructions(self):
        """Affiche les instructions d'utilisation"""
        self.interface.clear_screen()
        
        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║         INSTRUCTIONS D'UTILISATION     ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ 📱 ÉTAPE 1: Ajouter comptes Instagram  ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • Utilisez l'option 2 du menu       ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • Entrez identifiant/mot de passe   ║{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 🤖 ÉTAPE 2: Démarrer l'automatisation  ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • Utilisez l'option 1 du menu       ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • Le script fonctionne 24h/24       ║{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💰 ÉTAPE 3: Gagner des CashCoins       ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • Les tâches s'exécutent auto       ║{COLORS['S']}")
        print(f"{COLORS['B']}║    • CashCoins ajoutés à votre solde   ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        
        print(f"{COLORS['J']}📞 Support: @Dahery👌sur Telegram{COLORS['S']}")
        print(f"{COLORS['J']}💰 Abonnement: 7000ar pour 7 jours{COLORS['S']}")
        print()
        
        self.interface.press_enter()

    def main_menu(self):
        """Boucle principale du menu"""
        while self.running:
            self.display_menu()

            choice = self.interface.get_choice("Choisissez une option")

            if choice == "1":
                self.start_automation()
            elif choice == "2":
                self.add_account()
            elif choice == "3":
                self.view_accounts()
            elif choice == "4":
                self.delete_account()
            elif choice == "5":
                self.show_instructions()
            elif choice == "0":
                self.quit_app()
            else:
                self.interface.show_message("❌ Choix invalide", "error")
                self.interface.press_enter()

    def start_automation(self):
        """Démarre l'automatisation"""
        self.interface.clear_screen()
        
        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║          MODE AUTOMATISATION          ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ 🤖 Bot activé 24h/24                  ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 📱 Aucune intervention nécessaire     ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💰 Gagnez des CashCoins automatiquement║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()

        try:
            accounts = self.account_manager.get_all_accounts()
            if not accounts:
                self.interface.show_message("❌ Aucun compte Instagram", "error")
                self.interface.show_message("📝 Ajoutez d'abord des comptes", "warning")
                self.interface.press_enter()
                return

            print(f"{COLORS['V']}[📊] {len(accounts)} compte(s) disponible(s){COLORS['S']}")
            print(f"{COLORS['J']}[⏹️] Ctrl+C pour arrêter{COLORS['S']}")
            print()
            
            self.interface.press_enter()
            
            # Démarrer l'automatisation
            start_smm_automation()
            
        except KeyboardInterrupt:
            self.interface.show_message("⏹️ Automatisation arrêtée", "warning")
        except Exception as e:
            self.interface.show_message(f"❌ Erreur: {e}", "error")
            self.interface.press_enter()

    def add_account(self):
        """Ajoute un compte Instagram"""
        self.interface.clear_screen()
        self.interface.show_message("👤 AJOUTER UN COMPTE INSTAGRAM", "info")

        username = self.interface.get_input("Nom d'utilisateur Instagram")
        password = self.interface.get_input("Mot de passe Instagram", is_password=True)

        if username and password:
            print(f"\n{COLORS['C']}[ℹ️] Connexion en cours...{COLORS['S']}")
            success = self.account_manager.connect_instagram_account(username, password)
            
            if success:
                self.interface.show_message("✅ Compte ajouté avec succès!", "success")
            else:
                self.interface.show_message("❌ Échec de la connexion", "error")
                self.interface.show_message("💡 Vérifiez identifiant/mot de passe", "warning")
        else:
            self.interface.show_message("❌ Champs vides", "error")

        self.interface.press_enter()

    def view_accounts(self):
        """Affiche les comptes"""
        self.interface.clear_screen()
        self.interface.show_message("📂 MES COMPTES INSTAGRAM", "info")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte enregistré", "warning")
        else:
            print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
            print(f"{COLORS['C']}║          COMPTES ENREGISTRÉS           ║{COLORS['S']}")
            print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
            
            for i, (username, _) in enumerate(accounts, 1):
                print(f"{COLORS['B']}║ {COLORS['V']}{i:2d}.{COLORS['S']} {username:<25} {COLORS['B']}║{COLORS['S']}")
            
            print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
            print(f"{COLORS['J']}📊 Total: {len(accounts)} compte(s){COLORS['S']}")

        self.interface.press_enter()

    def delete_account(self):
        """Supprime un compte"""
        self.interface.clear_screen()
        self.interface.show_message("🗑️ SUPPRIMER UN COMPTE", "warning")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte à supprimer", "warning")
            self.interface.press_enter()
            return

        for i, (username, _) in enumerate(accounts, 1):
            print(f"  {COLORS['V']}[{i}] {username}{COLORS['S']}")

        choice = self.interface.get_input("Numéro à supprimer (0 pour annuler)")

        if choice == "0":
            self.interface.show_message("❌ Suppression annulée", "warning")
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                username = accounts[index][0]
                if self.account_manager.delete_account(index):
                    self.interface.show_message(f"✅ {username} supprimé", "success")
                else:
                    self.interface.show_message(f"❌ Erreur suppression", "error")
            else:
                self.interface.show_message("❌ Numéro invalide", "error")
        else:
            self.interface.show_message("❌ Choix invalide", "error")

        self.interface.press_enter()

    def quit_app(self):
        """Quitte l'application"""
        self.interface.clear_screen()
        
        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║            AU REVOIR ! 👋             ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║     Merci d'utiliser SmmKingdomTask   ║{COLORS['S']}")
        print(f"{COLORS['B']}║          Développé par Dah Ery         ║{COLORS['S']}")
        print(f"{COLORS['B']}║     📞 Contact: @DahEry sur Telegram   ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        
        self.running = False

def main():
    """Fonction principale"""
    try:
        app = SmmKingdomApp()
        
        # Écran de bienvenue
        app.show_welcome()
        
        # Vérification licence (BLOQUE si non activé)
        if not app.verify_license():
            return

        # Menu principal
        app.main_menu()
        
    except KeyboardInterrupt:
        print(f"\n{COLORS['J']}👋 Au revoir!{COLORS['S']}")
    except Exception as e:
        print(f"{COLORS['R']}💥 Erreur: {e}{COLORS['S']}")
        print(f"{COLORS['J']}📞 Contactez @DahEry sur Telegram{COLORS['S']}")

if __name__ == "__main__":
    main()
