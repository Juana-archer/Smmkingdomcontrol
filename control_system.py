# control_system.py - SYSTÈME DE CONTRÔLE DAH ERY
import requests
import json
import time
import os
import sys
from datetime import datetime
from config import COLORS

class ControlSystem:
    def __init__(self):
        self.user_id = self.get_user_id()
        self.license_url = "https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/license.json"
        self.users_url = "https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/users.json"

    def get_user_id(self):
        """Génère un ID unique pour chaque utilisateur"""
        try:
            # Essaye de lire l'ID existant
            with open('/data/data/com.termux/files/usr/etc/smm_user_id', 'r') as f:
                return f.read().strip()
        except:
            # Crée un nouvel ID
            import uuid
            user_id = str(uuid.uuid4())
            try:
                with open('/data/data/com.termux/files/usr/etc/smm_user_id', 'w') as f:
                    f.write(user_id)
            except:
                pass
            return user_id

    def check_license(self):
        """Vérifie la licence - BLOQUE si non activé"""
        try:
            # Vérifier d'abord le fichier de contrôle général
            response = requests.get(self.license_url, timeout=10)
            control_data = response.json()
            
            if not control_data.get("active", True):
                self.show_blocked_message("❌ Script désactivé par Dah Ery")
                return False, "Script désactivé"
            
            # Vérifier les utilisateurs bannis
            banned_users = control_data.get("banned_users", [])
            if self.user_id in banned_users:
                self.show_blocked_message("🚫 Accès révoqué par Dah Ery")
                return False, "Accès révoqué"
            
            # Vérifier l'abonnement utilisateur
            user_status = self.check_user_subscription()
            
            if user_status == "new_user":
                # NOUVEL UTILISATEUR - BLOQUER COMPLÈTEMENT
                return self.first_time_setup()
            elif user_status == "active":
                # UTILISATEUR ACTIVÉ - Calculer temps restant
                return self.calculate_time_remaining()
            elif user_status == "expired":
                # ABONNEMENT EXPIRÉ - BLOQUER
                self.show_expired_message()
                return False, "Abonnement expiré"
            else:
                self.show_blocked_message("❌ Erreur de vérification de licence")
                return False, "Erreur vérification"
            
        except Exception as e:
            self.show_blocked_message(f"❌ Erreur connexion: {e}")
            return False, f"Erreur: {e}"

    def check_user_subscription(self):
        """Vérifie le statut d'abonnement de l'utilisateur"""
        try:
            # Charger les données utilisateurs depuis GitHub
            response = requests.get(self.users_url, timeout=10)
            users_data = response.json()
            
            user_info = users_data.get(self.user_id, {})
            
            if not user_info:
                return "new_user"  # Nouvel utilisateur non activé
            elif user_info.get("status") == "active":
                # Vérifier si l'abonnement est encore valide
                expire_date = user_info.get("expire_date")
                if expire_date and datetime.now() < datetime.strptime(expire_date, "%Y-%m-%d"):
                    return "active"
                else:
                    return "expired"
            else:
                return "expired"
                
        except:
            return "new_user"  # En cas d'erreur, considérer comme nouveau

    def first_time_setup(self):
        """Configuration pour les nouveaux utilisateurs - BLOQUE LE SCRIPT"""
        print(f"\n{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['C']}║           ACTIVATION REQUISE           ║{COLORS['S']}")
        print(f"{COLORS['C']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ 🔑 VOTRE USER ID: {self.user_id}{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 📞 Contactez: @DahEry sur Telegram     ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💰 Prix: 5€ pour 7 jours d'accès       ║{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💳 Méthodes de paiement:               ║{COLORS['S']}")
        print(f"{COLORS['B']}║   • PayPal                             ║{COLORS['S']}")
        print(f"{COLORS['B']}║   • Crypto (USDT)                      ║{COLORS['S']}")
        print(f"{COLORS['B']}║   • Mobile Money                       ║{COLORS['S']}")
        print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        
        print(f"{COLORS['J']}📋 PROCÉDURE D'ACTIVATION:{COLORS['S']}")
        print(f"{COLORS['B']}1. Contactez @DahEry sur Telegram{COLORS['S']}")
        print(f"{COLORS['B']}2. Envoyez votre USER ID + preuve de paiement{COLORS['S']}")
        print(f"{COLORS['B']}3. Recevez l'activation sous 24h{COLORS['S']}")
        print()
        
        # Sauvegarder les données utilisateur localement
        self.save_user_data()
        
        # BLOQUER COMPLÈTEMENT LE SCRIPT
        input(f"{COLORS['R']}⏎ Appuyez sur Entrée pour quitter...{COLORS['S']}")
        sys.exit(1)  # Quitte complètement le script

    def show_blocked_message(self, reason):
        """Affiche un message de blocage et quitte"""
        print(f"\n{COLORS['R']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['R']}║              ACCÈS BLOQUÉ              ║{COLORS['S']}")
        print(f"{COLORS['R']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ {reason}{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 📞 Contactez @DahEry sur Telegram      ║{COLORS['S']}")
        print(f"{COLORS['R']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        sys.exit(1)

    def show_expired_message(self):
        """Affiche un message d'expiration et quitte"""
        print(f"\n{COLORS['R']}╔════════════════════════════════════════╗{COLORS['S']}")
        print(f"{COLORS['R']}║           ABONNEMENT EXPIRÉ            ║{COLORS['S']}")
        print(f"{COLORS['R']}╠════════════════════════════════════════╣{COLORS['S']}")
        print(f"{COLORS['B']}║ Votre abonnement de 7 jours a expiré   ║{COLORS['S']}")
        print(f"{COLORS['B']}║                                        ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 💰 Renouvellement: 5€ pour 7 jours     ║{COLORS['S']}")
        print(f"{COLORS['B']}║ 📞 Contactez @DahEry sur Telegram      ║{COLORS['S']}")
        print(f"{COLORS['R']}╚════════════════════════════════════════╝{COLORS['S']}")
        print()
        sys.exit(1)

    def calculate_time_remaining(self):
        """Calcule le temps restant de l'abonnement"""
        try:
            response = requests.get(self.users_url, timeout=10)
            users_data = response.json()
            
            user_info = users_data.get(self.user_id, {})
            expire_date = user_info.get("expire_date")
            
            if expire_date:
                expire_datetime = datetime.strptime(expire_date, "%Y-%m-%d")
                current_datetime = datetime.now()
                
                if current_datetime > expire_datetime:
                    days_passed = (current_datetime - expire_datetime).days
                    self.show_expired_message()
                    return False, f"Expiré depuis {days_passed} jour(s)"
                
                time_left = expire_datetime - current_datetime
                days = time_left.days
                hours = time_left.seconds // 3600
                
                return True, f"✅ Abonnement valide - {days}j {hours}h restantes"
            
            return False, "❌ Date d'expiration manquante"
            
        except Exception as e:
            return False, f"❌ Erreur calcul: {e}"

    def save_user_data(self):
        """Sauvegarde les données utilisateur localement"""
        user_data = {
            "user_id": self.user_id,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending_activation",
            "contact_info": "@DahEry sur Telegram",
            "price": "5€ pour 7 jours"
        }
        
        try:
            with open('user_data.json', 'w') as f:
                json.dump(user_data, f, indent=2)
        except:
            pass

    def get_user_limits(self):
        """Retourne les limites de l'utilisateur"""
        return {
            "max_accounts": 10,
            "max_tasks_per_day": 100,
            "subscription_days": 7
        }

    def send_usage_report(self, action, details):
        """Envoie un rapport d'utilisation à Dah Ery"""
        try:
            report = {
                "user_id": self.user_id,
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "version": "3.0"
            }

            # Affiche le rapport localement
            print(f"[📊] Rapport pour Dah Ery: {action}")

        except Exception as e:
            print(f"[⚠️] Erreur envoi rapport: {e}")
