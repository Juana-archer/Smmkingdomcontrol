# control_system.py - SYSTÈME DE CONTRÔLE DAH ERY
import requests
import json
import time
import hashlib
import uuid
import os
from datetime import datetime, timedelta
from config import COLORS

class ControlSystem:
    def __init__(self):
        self.machine_id = self.get_machine_id()  # Renommé pour plus de clarté
        self.license_url = "https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/license.json"
        self.local_license_file = "local_license.json"

    def get_machine_id(self):
        """Génère un ID unique basé sur la machine"""
        try:
            # Essayer de lire l'ID existant
            if os.path.exists("machine_id.txt"):
                with open("machine_id.txt", "r") as f:
                    machine_id = f.read().strip()
                    return machine_id
            
            # Générer un nouvel ID unique
            machine_info = str(uuid.getnode()) + str(os.path.exists)
            machine_id = hashlib.md5(machine_info.encode()).hexdigest()[:12]
            
            # Sauvegarder l'ID
            with open("machine_id.txt", "w") as f:
                f.write(machine_id)
            
            return machine_id
            
        except Exception as e:
            # Fallback simple
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:12]

    def check_license(self):
        """Vérifie la licence avec limitation par date"""
        try:
            print(f"\n{COLORS['C']}" + "="*50)
            print("🔍 VÉRIFICATION DE LA LICENCE")
            print("="*50 + f"{COLORS['S']}")
            
            print(f"{COLORS['J']}📱 Votre ID Machine: {self.machine_id}{COLORS['S']}")
            
            # Charge la licence depuis GitHub
            response = requests.get(self.license_url, timeout=10)
            license_data = response.json()

            # Vérifie si l'ID machine est autorisé
            authorized_users = license_data.get("authorized_users", {})
            
            if self.machine_id in authorized_users:
                user_data = authorized_users[self.machine_id]
                
                # Vérification date d'expiration
                expire_date_str = user_data.get("expire_date", "2099-12-31")
                expire_time_str = user_data.get("expire_time", "23:59")
                
                # Combine date et heure
                expire_datetime = datetime.strptime(f"{expire_date_str} {expire_time_str}", "%Y-%m-%d %H:%M")
                current_datetime = datetime.now()

                if current_datetime > expire_datetime:
                    days_passed = (current_datetime - expire_datetime).days
                    return False, f"📅 Abonnement expiré depuis {days_passed} jour(s)\n📞 Contactez @DahEry sur Telegram"

                # Calcul du temps restant
                time_left = expire_datetime - current_datetime
                days = time_left.days
                hours = time_left.seconds // 3600
                minutes = (time_left.seconds % 3600) // 60

                # Informations supplémentaires
                status = user_data.get("status", "active")
                plan = user_data.get("plan", "standard")
                
                return True, f"✅ Licence {plan} - {days}j {hours}h {minutes}m restantes"

            else:
                # ID non autorisé
                return False, f"❌ ACCÈS BLOQUÉ\n📞 Contactez @DahEry sur Telegram\n🔑 ID: {self.machine_id}"

        except Exception as e:
            # Mode hors ligne - vérification locale
            return self.check_local_license()

    def check_local_license(self):
        """Vérification locale en cas de problème de connexion"""
        try:
            if os.path.exists(self.local_license_file):
                with open(self.local_license_file, 'r') as f:
                    local_data = json.load(f)
                
                authorized_users = local_data.get("authorized_users", {})
                if self.machine_id in authorized_users:
                    user_data = authorized_users[self.machine_id]
                    expire_date = user_data.get("expire_date", "2099-12-31")
                    return True, f"🔶 Mode local - Valide jusqu'au {expire_date}"
                else:
                    return False, f"❌ Licence locale non valide\n🔑 ID: {self.machine_id}"
            else:
                return False, f"👋 Nouvel utilisateur\n🔑 Votre ID: {self.machine_id}\n📞 Contactez @DahEry"

        except Exception as e:
            return False, f"❌ Erreur vérification licence: {e}"

    def get_user_limits(self):
        """Récupère les limites selon le plan"""
        try:
            response = requests.get(self.license_url, timeout=10)
            license_data = response.json()

            authorized_users = license_data.get("authorized_users", {})
            
            if self.machine_id in authorized_users:
                user_data = authorized_users[self.machine_id]
                plan = user_data.get("plan", "standard")
                
                # Définir les limites selon le plan
                plans_limits = {
                    "basic": {"max_accounts": 100, "daily_tasks": 1000},
                    "standard": {"max_accounts": 200, "daily_tasks": 1000},
                    "premium": {"max_accounts": 300, "daily_tasks": 1000},
                    "vip": {"max_accounts": 400, "daily_tasks": 10000}
                }
                
                limits = plans_limits.get(plan, plans_limits["standard"])
                limits["features"] = ["instagram", "telegram"]
                limits["user_level"] = plan
                
                return limits
            else:
                # Plan par défaut si non autorisé
                return {
                    "max_accounts": 0,
                    "daily_tasks": 0,
                    "features": [],
                    "user_level": "none"
                }

        except:
            # Valeurs par défaut en cas d'erreur
            return {
                "max_accounts": 0,
                "daily_tasks": 0,
                "features": [],
                "user_level": "none"
            }

    def send_usage_report(self, action, details):
        """Envoie un rapport d'utilisation"""
        try:
            report = {
                "machine_id": self.machine_id,
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "version": "3.0"
            }

            print(f"{COLORS['B']}[📊] Rapport: {action}{COLORS['S']}")

        except Exception as e:
            print(f"{COLORS['R']}[⚠️] Erreur envoi rapport: {e}{COLORS['S']}")

    def first_time_setup(self):
        """Configuration première utilisation"""
        try:
            if os.path.exists('user_data.json'):
                return False
        except:
            pass

        # NOUVEL UTILISATEUR
        print(f"\n{COLORS['C']}" + "="*60)
        print("👋 BIENVENUE SUR SMM KINGDOM - DAH ERY")
        print("="*60 + f"{COLORS['S']}")

        print(f"{COLORS['J']}📞 POUR ACTIVER VOTRE ACCÈS:{COLORS['S']}")
        print(f"{COLORS['B']}1. Contactez @DahEry sur Telegram{COLORS['S']}")
        print(f"{COLORS['B']}2. Envoyez-lui votre ID Machine ci-dessous{COLORS['S']}")
        print(f"{COLORS['B']}3. Choisissez votre forfait{COLORS['S']}")
        print(f"{COLORS['B']}4. Recevez l'activation instantanée{COLORS['S']}")

        print(f"\n{COLORS['V']}🔑 VOTRE ID MACHINE: {self.machine_id}{COLORS['S']}")

        # Sauvegarde les données utilisateur
        user_data = {
            "machine_id": self.machine_id,
            "first_use": datetime.now().isoformat(),
            "status": "pending_activation"
        }

        try:
            contact = input(f"\n{COLORS['o']}[?] Votre pseudo Telegram: {COLORS['B']}")
            user_data["contact_info"] = contact
        except:
            user_data["contact_info"] = "Non spécifié"

        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)

        print(f"\n{COLORS['V']}✅ CONFIGURATION TERMINÉE!{COLORS['S']}")
        print(f"{COLORS['J']}📞 Contactez @DahEry sur Telegram pour activation{COLORS['S']}")
        
        input(f"\n{COLORS['o']}Appuyez sur Entrée pour continuer...{COLORS['S']}")
        
        return True

    def display_license_info(self):
        """Affiche les informations de licence"""
        success, message = self.check_license()
        
        print(f"\n{COLORS['C']}" + "="*50)
        print("📋 INFORMATIONS DE LICENCE")
        print("="*50 + f"{COLORS['S']}")
        
        print(f"{COLORS['B']}🔑 ID Machine: {self.machine_id}{COLORS['S']}")
        print(f"{COLORS['V']}📊 Statut: {message}{COLORS['S']}")
        
        # Afficher les limites
        limits = self.get_user_limits()
        if limits["max_accounts"] > 0:
            print(f"{COLORS['J']}📈 Limites: {limits['max_accounts']} comptes, {limits['daily_tasks']} tâches/jour{COLORS['S']}")
        
        if not success:
            print(f"\n{COLORS['J']}💡 Pour activer:{COLORS['S']}")
            print(f"{COLORS['B']}1. Contactez @DahEry sur Telegram")
            print(f"2. Envoyez votre ID Machine")
            print(f"3. Choisissez la durée{COLORS['S']}")
        
        return success

# Fonction utilitaire pour vérifier la licence
def verify_license():
    """Fonction pour vérifier la licence au démarrage"""
    control = ControlSystem()
    
    # Vérifie si première utilisation
    control.first_time_setup()
    
    # Vérifie la licence
    success, message = control.check_license()
    
    if not success:
        print(f"\n{COLORS['R']}" + "="*50)
        print("🚫 ACCÈS REFUSÉ")
        print("="*50)
        print(f"{message}{COLORS['S']}")
        print(f"\n{COLORS['J']}💡 Contactez @DahEry sur Telegram{COLORS['S']}")
        input(f"\n{COLORS['o']}Appuyez sur Entrée pour quitter...{COLORS['S']}")
        exit()
    
    return control
