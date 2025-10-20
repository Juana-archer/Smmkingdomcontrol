# control_system.py - SYSTÈME DE CONTRÔLE DAH ERY
import requests                                            import json
import time
from datetime import datetime
from config import COLORS

class ControlSystem:
    def __init__(self):
        self.user_id = self.get_user_id()                          self.license_url = "https://raw.githubusercontent.com/Juana-archa/SmmKingdomControl/main/license.json"

    def get_user_id(self):
        """Génère un ID unique pour chaque utilisateur"""
        try:                                                           # Essaye de lire l'ID existant
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
        """Vérifie la licence avec expiration date/heure"""
        try:
            # Charge la licence
            response = requests.get(self.license_url, timeout=10)
            control_data = response.json()

            # Vérification principale
            if not control_data.get("active", True):
                return False, "❌ Script désactivé par Dah Ery"

            # Vérification bannissement
            banned_users = control_data.get("banned_users", [])
            if self.user_id in banned_users:
                return False, "🚫 Accès révoqué par Dah Ery"

            # Vérification date d'expiration
            expire_date = control_data.get("expire_date", "2099-12-31")
            expire_time = control_data.get("expire_time", "23:59")

            # Combine date et heure
            expire_datetime = datetime.strptime(f"{expire_date} {expire_time}", "%Y-%m-%d %H:%M")
            current_datetime = datetime.now()

            if current_datetime > expire_datetime:
                days_left = (current_datetime - expire_datetime).days
                return False, f"📅 Abonnement expiré depuis {abs(days_left)} jour(s) - Contactez Dah Ery"

            # Calcul du temps restant
            time_left = expire_datetime - current_datetime
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60

            return True, f"✅ Abonnement valide - {days}j {hours}h {minutes}m restantes"

        except Exception as e:
            # Mode hors ligne - vérification locale
            return self.check_local_license()

    def check_local_license(self):
        """Vérification locale en cas de problème de connexion"""
        try:
            with open('local_license.json', 'r') as f:
                local_data = json.load(f)
                if not local_data.get("active", True):
                    return False, "❌ Licence locale désactivée"
                return True, "🔶 Mode local - Connexion impossible"
        except:
            # Première utilisation
            local_data = {
                "active": True,
                "first_use": datetime.now().isoformat(),
                "user_id": self.user_id,
                "created_by": "Dah Ery"
            }
            with open('local_license.json', 'w') as f:
                json.dump(local_data, f)
            return True, "👋 Nouvel utilisateur - Bienvenue!"

    def get_user_limits(self):
        """Récupère les limites depuis le serveur de Dah Ery"""
        try:
            response = requests.get(self.license_url, timeout=10)
            license_data = response.json()

            return {
                "max_accounts": license_data.get("max_accounts", 5),
                "daily_tasks": license_data.get("daily_tasks", 30),
                "features": ["instagram", "telegram"],
                "user_level": "default"
            }

        except:
            # Valeurs par défaut en cas d'erreur
            return {
                "max_accounts": 5,
                "daily_tasks": 30,
                "features": ["instagram", "telegram"],
                "user_level": "default"
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

    def first_time_setup(self):
        """Configuration première utilisation"""
        try:
            # Vérifie si déjà configuré
            with open('user_data.json', 'r') as f:
                return False
        except:
            # NOUVEL UTILISATEUR
            print(f"\n{COLORS['C']}" + "="*50)
            print("👋 NOUVEL UTILISATEUR DÉTECTÉ")
            print("="*50 + f"{COLORS['S']}")

            print(f"{COLORS['J']}📞 POUR ACTIVER VOTRE ABONNEMENT:{COLORS['S']}")
            print(f"{COLORS['B']}1. Contactez Dah Ery sur WhatsApp/Facebook{COLORS['S']}")
            print(f"{COLORS['B']}2. Envoyez-lui votre User ID ci-dessous{COLORS['S']}")
            print(f"{COLORS['B']}3. Payez l'abonnement (5€/semaine){COLORS['S']}")
            print(f"{COLORS['V']}4. Attendez l'activation par Dah Ery{COLORS['S']}")

            print(f"\n{COLORS['C']}🔑 VOTRE USER ID: {self.user_id}{COLORS['S']}")
            print(f"{COLORS['J']}💰 PRIX: 5€ pour 7 jours{COLORS['S']}")

            # Sauvegarde les données utilisateur
            user_data = {
                "user_id": self.user_id,
                "first_use": datetime.now().isoformat(),
                "status": "pending",
                "contact_info": ""
            }

            contact = input(f"\n{COLORS['o']}[?] Votre nom pour contact: {COLORS['B']}")
            user_data["contact_info"] = contact

            with open('user_data.json', 'w') as f:
                json.dump(user_data, f, indent=2)

            print(f"\n{COLORS['V']}✅ DEMANDE ENREGISTRÉE!{COLORS['S']}")
            print(f"{COLORS['J']}⏳ Contactez Dah Ery pour activation...{COLORS['S']}")

            return True
