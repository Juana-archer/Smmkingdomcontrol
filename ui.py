# ui.py
import os
from config import COLORS

class Interface:
    def __init__(self):
        self.logo = f"""
{COLORS['o']}═════════════════════════════════════════     {COLORS['vi']}┌────────────────────────────────┐
│        SMM KINGDOM TASK        │
│          {COLORS['V']}Version 3.0{COLORS['vi']}           │                                                         │                                │
│      {COLORS['J']}Contrôlé par Dah Ery{COLORS['vi']}      │
└────────────────────────────────┘
{COLORS['o']}═════════════════════════════════════════"""

    def clear_screen(self):
        os.system('clear')                                         print(self.logo)

    def display_menu(self):
        menu_items = [
            ("1", "🚀 Démarrer le bot Telegram"),
            ("2", "👤 Ajouter compte Instagram"),
            ("3", "📂 Voir mes comptes"),
            ("4", "🗑️  Supprimer un compte"),
            ("5", "🍪 Voir les cookies"),
            ("0", "❌ Quitter")
        ]

        print(f"{COLORS['o']}═════════════════════════════════════════")
        print(f"{COLORS['B']}           MENU PRINCIPAL")
        print(f"{COLORS['o']}═════════════════════════════════════════")

        for key, desc in menu_items:
            print(f"{COLORS['o']}[{COLORS['V']}{key}{COLORS['o']}] {desc}")

        print(f"{COLORS['o']}═════════════════════════════════════════")

    def get_choice(self, prompt="Choix"):
        return input(f"{COLORS['o']}[{COLORS['V']}?{COLORS['o']}] {prompt}: {COLORS['B']}")

    def show_message(self, message, msg_type="info"):
        colors = {
            "info": COLORS['C'],
            "success": COLORS['V'],
            "error": COLORS['R'],
            "warning": COLORS['J']
        }
        color = colors.get(msg_type, COLORS['B'])
        print(f"{color}{message}{COLORS['S']}")

    def press_enter(self):
        input(f"{COLORS['o']}[{COLORS['V']}↵{COLORS['o']}] Appuyez sur Entrée...")
