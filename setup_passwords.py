# setup_passwords.py - SAUVEGARDE DES MOTS DE PASSE UNE SEULE FOIS
from account_manager import AccountManager

def setup_passwords():
    """Sauvegarde les mots de passe une fois pour toutes"""
    manager = AccountManager()

    print("🔐 CONFIGURATION DES MOTS DE PASSE")
    print("Une seule fois - pour la réparation automatique")
    print("=" * 50)

    accounts = manager.get_all_accounts()

    for username, cookies_str in accounts:
        print(f"\n📝 Compte: {username}")
        password = input("   🔑 Mot de passe (laisser vide pour passer): ")

        if password:
            manager.save_account_password(username, password)
        else:
            print("   ⏭️ Passé")

    print("\n✅ Configuration terminée!")
    print("Le système pourra maintenant réparer automatiquement les cookies expirés")

if __name__ == "__main__":
    setup_passwords()
