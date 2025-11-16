#!/usr/bin/env python3
# main.py - Script principal SmmKingdomTask
import asyncio
import json
import os
import sys
import time
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
                print(f"{COLORS['J']}[👤] Votre ID: {self.control.user_id}{COLORS['S']}")

            self.interface.press_enter()
            return False

        self.interface.show_message(f"✅ {message}", "success")
        self.interface.show_message("👑 Contrôlé par Dah Ery", "info")
        self.interface.press_enter()
        return True

    def display_menu(self):
        """Affiche le menu principal"""
        self.interface.clear_screen()

        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║           SMM KINGDOM TASK v3.0        ║{COLORS['S']}")
        print(f"{COLORS['C']}║           Contrôlé par Dah Ery         ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║  1. 🤖 Démarrer l'automatisation       ║{COLORS['S']}")
        print(f"{COLORS['B']}║  2. 👤 Ajouter un compte Instagram     ║{COLORS['S']}")
        print(f"{COLORS['B']}║  3. 📂 Voir mes comptes                ║{COLORS['S']}")
        print(f"{COLORS['B']}║  4. 🔍 Voir statut détaillé            ║{COLORS['S']}")
        print(f"{COLORS['B']}║  5. 🚫 Comptes avec problèmes          ║{COLORS['S']}")
        print(f"{COLORS['B']}║  6. 🗑️  Supprimer un compte            ║{COLORS['S']}")
        print(f"{COLORS['B']}║  7. 🍪 Voir les cookies                ║{COLORS['S']}")
        print(f"{COLORS['B']}║  0. 🚪 Quitter                         ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()

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
                self.view_detailed_status()
            elif choice == "5":
                self.view_problem_accounts()
            elif choice == "6":
                self.delete_account()
            elif choice == "7":
                self.view_cookies()
            elif choice == "0":
                self.quit_app()
            else:
                self.interface.show_message("❌ Choix invalide", "error")
                self.interface.press_enter()

    def start_automation(self):
        """Démarre l'automatisation SMM Kingdom"""
        self.interface.clear_screen()
        self.interface.show_message("🤖 AUTOMATISATION SMM KINGDOM", "info")

        try:
            # Vérifier qu'il y a des comptes Instagram
            accounts = self.account_manager.get_all_accounts()
            if not accounts:
                self.interface.show_message("❌ Aucun compte Instagram disponible", "error")
                self.interface.show_message("📝 Ajoutez d'abord un compte avec l'option 2", "warning")
                self.interface.press_enter()
                return

            # Vérifier les comptes problématiques avant de démarrer
            from instagram_tasks import get_problem_accounts
            problem_accounts = get_problem_accounts()

            if problem_accounts:
                self.interface.show_message("⚠️  Comptes avec problèmes détectés:", "warning")
                for username, info in problem_accounts.items():
                    print(f"   🚫 {username}: {info.get('reason', 'Raison inconnue')}")

                print()
                self.interface.show_message("💡 Il est recommandé de résoudre les problèmes d'abord", "info")
                choice = self.interface.get_input("Démarrer quand même ? (o/n)").lower()

                if choice != 'o':
                    return

            self.interface.show_message(f"📊 {len(accounts)} compte(s) disponible(s)", "success")
            self.interface.show_message("🔄 Démarrage de l'automatisation...", "info")

            print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
            print(f"{COLORS['C']}║          MODE AUTOMATISATION           ║{COLORS['S']}")
            print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
            print(f"{COLORS['B']}║ 📋 Tasks → 📷 Instagram               ║{COLORS['S']}")
            print(f"{COLORS['B']}║ 🔄 Teste chaque compte pour tâches    ║{COLORS['S']}")
            print(f"{COLORS['B']}║ ⚡ Exécute tâches automatiquement      ║{COLORS['S']}")
            print(f"{COLORS['B']}║ ✅ Clique 'Completed'                  ║{COLORS['S']}")
            print(f"{COLORS['B']}║ 🔁 Boucle infinie 24h/24              ║{COLORS['S']}")
            print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
            print()

            self.interface.show_message("⏹️  Tapez Ctrl+C pour arrêter l'automatisation", "warning")
            self.interface.press_enter()

            # Démarrer l'automatisation
            start_smm_automation()

        except KeyboardInterrupt:
            self.interface.show_message("⏹️ Automatisation arrêtée par l'utilisateur", "warning")
        except Exception as e:
            self.interface.show_message(f"❌ Erreur: {e}", "error")
            self.interface.press_enter()

    def add_account(self):
        """Ajoute un compte Instagram"""
        self.interface.clear_screen()
        self.interface.show_message("👤 AJOUTER UN COMPTE INSTAGRAM", "info")

        username = self.interface.get_input("Nom d'utilisateur Instagram")
        if not username:
            self.interface.show_message("❌ Nom d'utilisateur requis", "error")
            self.interface.press_enter()
            return

        # CORRECTION : Afficher le mot de passe en clair dans Termux
        print(f"{COLORS['B']}[🔓] Mot de passe Instagram: {COLORS['S']}", end="", flush=True)
        password = input()

        if not password:
            self.interface.show_message("❌ Mot de passe requis", "error")
            self.interface.press_enter()
            return

        print(f"\n{COLORS['C']}[ℹ️] Résumé du compte:{COLORS['S']}")
        print(f"{COLORS['B']}   Utilisateur: {username}{COLORS['S']}")
        print(f"{COLORS['B']}   Mot de passe: {password}{COLORS['S']}")  # Afficher en clair pour confirmation
        print()

        confirm = self.interface.get_input("Confirmer l'ajout? (o/n)").lower()

        if confirm == 'o' or confirm == 'oui':
            # CORRECTION : Utiliser AccountManager au lieu de la fonction supprimée
            success = self.account_manager.connect_instagram_account(username, password)

            if success:
                self.interface.show_message("✅ Compte ajouté avec succès!", "success")
                print(f"{COLORS['J']}🔍 Vérification du statut du compte...{COLORS['S']}")

                # CORRECTION : Utiliser validate_session au lieu de check_single_account_status
                status = self.account_manager.validate_session(username)

                if status:
                    self.interface.show_message("🎉 Compte fonctionnel ! Prêt pour l'automatisation.", "success")
                else:
                    self.interface.show_message("📧 Vérification requise. Connecte-toi manuellement sur Instagram.", "warning")
            else:
                self.interface.show_message("❌ Échec de l'ajout du compte", "error")
        else:
            self.interface.show_message("❌ Ajout annulé", "warning")

        self.interface.press_enter()

    def view_accounts(self):
        """Affiche les comptes simplement"""
        self.interface.clear_screen()
        self.interface.show_message("📂 MES COMPTES INSTAGRAM", "info")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte enregistré", "warning")
            self.interface.show_message("💡 Utilisez l'option 2 pour ajouter un compte", "info")
        else:
            from instagram_tasks import get_problem_accounts
            problem_accounts = get_problem_accounts()

            print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
            print(f"{COLORS['C']}║          COMPTES INSTAGRAM             ║{COLORS['S']}")
            print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")

            # CORRECTION : Itération correcte sur le dictionnaire
            for i, (username, account_data) in enumerate(accounts.items(), 1):
                cookies = account_data.get('cookies', '')
                # Vérifier si le compte a des problèmes
                if username in problem_accounts:
                    status_icon = "🚫"
                    status_text = "PROBLÈME"
                    color = COLORS['R']
                else:
                    status_icon = "✅"
                    status_text = "ACTIF"
                    color = COLORS['V']

                print(f"{COLORS['B']}║ {color}{i:2d}. {username:<20} {status_icon} {status_text} {COLORS['B']}║{COLORS['S']}")

            print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")

            # Statistiques
            problem_count = len([acc for acc in accounts if acc in problem_accounts])
            working_count = len(accounts) - problem_count

            print(f"{COLORS['J']}📊 Total: {len(accounts)} compte(s) | {working_count}✅ actifs | {problem_count}🚫 problèmes{COLORS['S']}")
            print(f"{COLORS['C']}💡 Utilisez l'option 4 pour voir les détails des problèmes{COLORS['S']}")

        self.interface.press_enter()

    def view_detailed_status(self):
        """Affiche le statut détaillé de tous les comptes"""
        self.interface.clear_screen()
        self.interface.show_message("🔍 STATUT DÉTAILLÉ DES COMPTES", "info")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte enregistré", "warning")
            self.interface.press_enter()
            return

        print(f"{COLORS['C']}╔══════════════════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║               STATUT DÉTAILLÉ DES COMPTES            ║{COLORS['S']}")
        print(f"{COLORS['C']}╠══════════════════════════════════════════════════════╣{COLORS['S']}")

        working_count = 0
        problem_count = 0

        # CORRECTION : Utiliser get_problem_accounts()
        from instagram_tasks import get_problem_accounts
        problem_accounts = get_problem_accounts()

        # CORRECTION : Itération correcte
        for i, (username, account_data) in enumerate(accounts.items(), 1):
            cookies = account_data.get('cookies', '')
            print(f"{COLORS['B']}║ {COLORS['J']}[{i}] {username:<25}{COLORS['S']}{COLORS['B']} ║{COLORS['S']}")

            # CORRECTION : Utiliser validate_session
            status = self.account_manager.validate_session(username)

            if status:
                status_icon = "✅"
                status_text = "FONCTIONNEL"
                color = COLORS['V']
                working_count += 1
            else:
                status_icon = "🔓"
                status_text = "PAS DE SESSION"
                color = COLORS['J']
                problem_count += 1

            print(f"{COLORS['B']}║   {color}{status_icon} {status_text:<20}{COLORS['S']}{COLORS['B']} ║{COLORS['S']}")

            # Afficher la raison si problème
            if not status and username in problem_accounts:
                reason = problem_accounts[username].get('reason', 'Raison inconnue')
                print(f"{COLORS['B']}║   📋 {reason:<35} {COLORS['B']}║{COLORS['S']}")

            print(f"{COLORS['B']}║{' ':52}║{COLORS['S']}")

        print(f"{COLORS['C']}╚══════════════════════════════════════════════════════╝{COLORS['S']}")

        # Résumé
        print(f"\n{COLORS['J']}📊 SYNTHÈSE: {working_count}✅ fonctionnels | {problem_count}🚫 problèmes{COLORS['S']}")

        if problem_count > 0:
            print(f"{COLORS['R']}💡 Conseil: Résous les problèmes des comptes avant de démarrer l'automatisation{COLORS['S']}")

        self.interface.press_enter()

    def view_problem_accounts(self):
        """Affiche seulement les comptes avec problèmes"""
        self.interface.clear_screen()
        self.interface.show_message("🚫 COMPTES AVEC PROBLÈMES", "warning")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte enregistré", "warning")
            self.interface.press_enter()
            return

        from instagram_tasks import get_problem_accounts
        problem_accounts = get_problem_accounts()

        problem_accounts_list = []
        # CORRECTION : Itération correcte
        for username, account_data in accounts.items():
            if username in problem_accounts:
                problem_accounts_list.append(username)

        if not problem_accounts_list:
            self.interface.show_message("🎉 Aucun compte avec problème détecté !", "success")
            self.interface.press_enter()
            return

        print(f"{COLORS['C']}╔══════════════════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║               COMPTES AVEC PROBLÈMES                 ║{COLORS['S']}")
        print(f"{COLORS['C']}╠══════════════════════════════════════════════════════╣{COLORS['S']}")

        for i, username in enumerate(problem_accounts_list, 1):
            reason = problem_accounts[username].get('reason', 'Raison inconnue')
            print(f"{COLORS['B']}║ {COLORS['R']}{i:2d}. {username:<25}{COLORS['S']}{COLORS['B']} ║{COLORS['S']}")
            print(f"{COLORS['B']}║   📋 {reason:<35} {COLORS['B']}║{COLORS['S']}")
            print(f"{COLORS['B']}║   💡 Connecte-toi manuellement sur Instagram{' ':8} {COLORS['B']}║{COLORS['S']}")
            print(f"{COLORS['B']}║{' ':52}║{COLORS['S']}")

        print(f"{COLORS['C']}╚══════════════════════════════════════════════════════╝{COLORS['S']}")

        print(f"\n{COLORS['R']}🔧 {len(problem_accounts_list)} compte(s) nécessitent une attention{COLORS['S']}")
        print(f"{COLORS['J']}💡 Résous ces problèmes avant de démarrer l'automatisation{COLORS['S']}")

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

        # Afficher la liste numérotée avec statuts
        from instagram_tasks import get_problem_accounts
        problem_accounts = get_problem_accounts()

        print(f"{COLORS['C']}Comptes disponibles:{COLORS['S']}")
        # CORRECTION : Itération correcte
        for i, (username, account_data) in enumerate(accounts.items(), 1):
            status_icon = "🚫" if username in problem_accounts else "✅"
            print(f"  {COLORS['V']}[{i}] {username} {status_icon}{COLORS['S']}")
        print()

        choice = self.interface.get_input("Numéro du compte à supprimer (0 pour annuler)")

        if choice == "0":
            self.interface.show_message("❌ Suppression annulée", "warning")
        elif choice.isdigit():
            index = int(choice) - 1
            usernames = list(accounts.keys())
            if 0 <= index < len(usernames):
                username = usernames[index]
                confirm = self.interface.get_input(f"Supprimer {username}? (o/n)").lower()

                if confirm == 'o' or confirm == 'oui':
                    if self.account_manager.delete_account(username):
                        self.interface.show_message(f"✅ {username} supprimé", "success")
                    else:
                        self.interface.show_message(f"❌ Erreur suppression {username}", "error")
                else:
                    self.interface.show_message("❌ Suppression annulée", "warning")
            else:
                self.interface.show_message("❌ Numéro invalide", "error")
        else:
            self.interface.show_message("❌ Choix invalide", "error")

        self.interface.press_enter()

    def view_cookies(self):
        """Affiche les cookies des comptes"""
        self.interface.clear_screen()
        self.interface.show_message("🍪 COOKIES DES COMPTES", "info")

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.interface.show_message("📭 Aucun compte", "warning")
        else:
            print(f"{COLORS['C']}╔══════════════════════════════════════════════════════════╗{COLORS['S']}")
            print(f"{COLORS['C']}║                     COOKIES DES COMPTES                  ║{COLORS['S']}")
            print(f"{COLORS['C']}╠══════════════════════════════════════════════════════════╣{COLORS['S']}")

            # CORRECTION : Itération correcte
            for i, (username, account_data) in enumerate(accounts.items(), 1):
                cookies_str = account_data.get('cookies', '')
                session_data = account_data.get('session_data', '')
                print(f"{COLORS['B']}║ {COLORS['V']}[{i}] {username}{COLORS['S']}{COLORS['B']} ║{COLORS['S']}")
                try:
                    if session_data:
                        session_info = json.loads(session_data)
                        if 'cookies' in session_info and 'sessionid' in session_info['cookies']:
                            session_id = session_info['cookies']['sessionid']
                            session_preview = session_id[:30] + '...' if len(session_id) > 30 else session_id
                            print(f"{COLORS['B']}║   Session: {session_preview:<25} {COLORS['B']}║{COLORS['S']}")
                        if 'cookies' in session_info and 'csrftoken' in session_info['cookies']:
                            csrf_token = session_info['cookies']['csrftoken']
                            csrf_preview = csrf_token[:20] + '...' if len(csrf_token) > 20 else csrf_token
                            print(f"{COLORS['B']}║   CSRF:    {csrf_preview:<25} {COLORS['B']}║{COLORS['S']}")
                    else:
                        print(f"{COLORS['B']}║   {COLORS['R']}PAS DE SESSION ACTIVE{' ':27} {COLORS['B']}║{COLORS['S']}")
                except:
                    print(f"{COLORS['B']}║   {COLORS['R']}ERREUR LECTURE SESSION{' ':27} {COLORS['B']}║{COLORS['S']}")
                print(f"{COLORS['B']}║{' ':56}║{COLORS['S']}")

            print(f"{COLORS['C']}╚══════════════════════════════════════════════════════════╝{COLORS['S']}")

        self.interface.press_enter()

    def quit_app(self):
        """Quitte l'application"""
        self.interface.clear_screen()

        print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║            AU REVOIR ! 👋             ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║    Merci d'utiliser SmmKingdomTask    ║{COLORS['S']}")
        print(f"{COLORS['B']}║        Développé par Dah Ery          ║{COLORS['S']}")
        print(f"{COLORS['B']}║    📞 Contact: @DahEry sur Telegram   ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()

        self.running = False

def main():
    """Fonction principale"""
    try:
        app = SmmKingdomApp()

        # Vérification de licence
        if not app.verify_license():
            print(f"{COLORS['R']}🚫 Application arrêtée - Licence invalide{COLORS['S']}")
            return

        # Lancement du menu principal
        app.main_menu()

    except KeyboardInterrupt:
        print(f"\n{COLORS['J']}👋 Arrêt de l'application{COLORS['S']}")
    except Exception as e:
        print(f"{COLORS['R']}💥 Erreur critique: {e}{COLORS['S']}")
        print(f"{COLORS['J']}📞 Contactez Dah Ery pour support{COLORS['S']}")

if __name__ == "__main__":
    main()
