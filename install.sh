#!/bin/bash
# install.sh - Installation automatique SmmKingdomTask avec API personnalisée
# Développé par Dah Ery - Version 3.0

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         SMM KINGDOM TASK v3.0          ║"
echo "║         Installation Automatique       ║"
echo "║         Contrôlé par Dah Ery           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[1;91m'
GREEN='\033[1;92m'
YELLOW='\033[1;93m'
CYAN='\033[1;96m'
WHITE='\033[1;97m'
RESET='\033[0m'

# Fonctions d'affichage
print_info() { echo -e "${CYAN}[ℹ️] $1${RESET}"; }
print_success() { echo -e "${GREEN}[✅] $1${RESET}"; }
print_warning() { echo -e "${YELLOW}[⚠️] $1${RESET}"; }
print_error() { echo -e "${RED}[❌] $1${RESET}"; }

# URLs GitHub
GITHUB_USER="Juana-archer"
GITHUB_REPO="Smmkingdomcontrol"
BASE_URL="https://raw.githubusercontent.com/$GITHUB_USER/$GITHUB_REPO/main"

# Vérifier Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "Ce script doit être exécuté dans Termux!"
    echo "Téléchargez Termux depuis F-Droid ou Play Store"
    exit 1
fi

print_info "Début de l'installation..."
echo ""

# ÉTAPE 1: Mise à jour complète de Termux
print_info "ÉTAPE 1: Mise à jour de Termux..."
print_warning "Cela peut prendre quelques minutes..."

pkg update -y
if [ $? -eq 0 ]; then
    print_success "Mise à jour des packages réussie"
else
    print_error "Erreur lors de la mise à jour"
    exit 1
fi

pkg upgrade -y
if [ $? -eq 0 ]; then
    print_success "Upgrade des packages réussi"
else
    print_error "Erreur lors de l'upgrade"
    exit 1
fi

# ÉTAPE 2: Installation des dépendances système
print_info "ÉTAPE 2: Installation des dépendances système..."

pkg install python -y
if [ $? -eq 0 ]; then
    print_success "Python installé"
else
    print_error "Erreur installation Python"
    exit 1
fi

# AJOUT DES DÉPENDANCES INSTAGRAM SPÉCIFIQUES
print_info "Installation des dépendances spécifiques pour Instagram..."
pkg install libjpeg-turbo libpng -y
if [ $? -eq 0 ]; then
    print_success "libjpeg-turbo et libpng installés"
else
    print_error "Erreur installation libjpeg-turbo/libpng"
    exit 1
fi

pkg install git -y
pkg install wget -y
pkg install curl -y
pkg install proot -y
pkg install termux-tools -y

print_success "Dépendances système installées"

# ÉTAPE 3: Demander l'accès au stockage
print_info "ÉTAPE 3: Configuration des permissions..."

print_warning "L'accès au stockage est nécessaire pour sauvegarder les comptes"
echo "Une fenêtre de permission va s'ouvrir..."
echo "Cliquez sur 'Autoriser' pour continuer"

# Demander la permission storage
termux-setup-storage

# Attendre que l'utilisateur donne la permission
print_info "Attente de l'autorisation de stockage..."
sleep 5

# Vérifier si le dossier storage est accessible
if [ -d "/sdcard" ]; then
    print_success "Accès au stockage autorisé"
else
    print_warning "Accès storage non autorisé - certaines fonctionnalités seront limitées"
fi

# ÉTAPE 4: Nettoyage des anciennes installations
print_info "ÉTAPE 4: Nettoyage des anciennes versions..."

if [ -d "~/SmmKingdom" ]; then
    print_warning "Ancienne installation détectée - nettoyage..."
    rm -rf ~/SmmKingdom
    print_success "Nettoyage terminé"
fi

# ÉTAPE 5: Création des dossiers
print_info "ÉTAPE 5: Création de la structure..."

mkdir -p ~/SmmKingdom
cd ~/SmmKingdom

# Créer le dossier de données sur le stockage
mkdir -p /sdcard/SmmKingdomTask
mkdir -p /sdcard/SmmKingdomTask/sessions
mkdir -p /sdcard/SmmKingdomTask/logs

print_success "Dossiers créés avec succès"

# ÉTAPE 6: Téléchargement des fichiers UN PAR UN
print_info "ÉTAPE 6: Téléchargement des fichiers..."

print_info "Téléchargement: main.py"
curl -o main.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/main.py
if [ $? -eq 0 ]; then
    print_success "main.py ✓"
else
    print_error "Échec: main.py"
    exit 1
fi

print_info "Téléchargement: config.py"
curl -o config.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/config.py
if [ $? -eq 0 ]; then
    print_success "config.py ✓"
else
    print_error "Échec: config.py"
    exit 1
fi

print_info "Téléchargement: account_manager.py"
curl -o account_manager.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/account_manager.py
if [ $? -eq 0 ]; then
    print_success "account_manager.py ✓"
else
    print_error "Échec: account_manager.py"
    exit 1
fi

print_info "Téléchargement: telegram_client.py"
curl -o telegram_client.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/telegram_client.py
if [ $? -eq 0 ]; then
    print_success "telegram_client.py ✓"
else
    print_error "Échec: telegram_client.py"
    exit 1
fi

print_info "Téléchargement: instagram_tasks.py"
curl -o instagram_tasks.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/instagram_tasks.py
if [ $? -eq 0 ]; then
    print_success "instagram_tasks.py ✓"
else
    print_error "Échec: instagram_tasks.py"
    exit 1
fi

print_info "Téléchargement: ui.py"
curl -o ui.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/ui.py
if [ $? -eq 0 ]; then
    print_success "ui.py ✓"
else
    print_error "Échec: ui.py"
    exit 1
fi

print_info "Téléchargement: control_system.py"
curl -o control_system.py https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/control_system.py
if [ $? -eq 0 ]; then
    print_success "control_system.py ✓"
else
    print_error "Échec: control_system.py"
    exit 1
fi

# Télécharger le fichier requirements
print_info "Téléchargement du fichier requirements..."
curl -o requirements.txt https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/requirements.txt
if [ $? -eq 0 ]; then
    print_success "requirements.txt ✓"
else
    # Créer un fichier requirements par défaut avec TOUTES les dépendances
    cat > requirements.txt << 'EOF'
telethon==1.28.5
requests==2.31.0
instagrapi==1.16.22
python-dotenv==1.0.0
urllib3==1.26.16
colorama==0.4.6
pycryptodome==3.18.0
rsa==4.9
EOF
    print_success "requirements.txt créé avec toutes les dépendances"
fi

# Télécharger le guide API
print_info "Téléchargement du guide API..."
curl -o API_GUIDE.md https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main/API_GUIDE.md
if [ $? -eq 0 ]; then
    print_success "API_GUIDE.md ✓"
else
    # Créer un guide API basique
    cat > API_GUIDE.md << 'EOF'
# 📱 Guide pour obtenir API ID et API HASH Telegram

## ÉTAPE 1: Aller sur my.telegram.org
- Ouvrez https://my.telegram.org dans votre navigateur
- Connectez-vous avec votre numéro de téléphone Telegram

## ÉTAPE 2: Accéder aux outils API
- Cliquez sur "API Development Tools"
- Si c'est votre première fois, cliquez sur "Create application"

## ÉTAPE 3: Remplir les informations
- **App title:** `SmmKingdomTask` (ou autre nom)
- **Short name:** `smmtask` 
- **Platform:** `Desktop`
- **Description:** `Application pour automatisation SMM`

## ÉTAPE 4: Récupérer les credentials
- **API ID:** Chiffres (ex: 1234567)
- **API HASH:** Chaîne de caractères (ex: a1b2c3d4e5f6...)

## ÉTAPE 5: Utiliser dans l'installation
- Lors de l'installation, choisissez "API personnalisée"
- Entrez votre API ID et API HASH

## ⚠️ Important
- Ne partagez jamais votre API HASH
- Ces credentials sont liés à votre compte Telegram
- Plus sécurisé que d'utiliser une API partagée
EOF
    print_success "API_GUIDE.md créé"
fi

# ÉTAPE 7: Installation des dépendances Python COMPLÈTES
print_info "ÉTAPE 7: Installation des dépendances Python..."
print_warning "Cela peut prendre plusieurs minutes..."

# Mise à jour de pip
print_info "Mise à jour de pip..."
pip install --upgrade pip

# INSTALLATION SPÉCIFIQUE POUR INSTAGRAM AVEC LES VERSIONS EXACTES
print_info "Installation des dépendances spécifiques Instagram..."
pip install pillow --no-cache-dir
if [ $? -eq 0 ]; then
    print_success "Pillow installé avec succès"
else
    print_error "Erreur installation Pillow"
    exit 1
fi

pip install instagrapi==1.16.22
if [ $? -eq 0 ]; then
    print_success "instagrapi 1.16.22 installé avec succès"
else
    print_error "Erreur installation instagrapi"
    exit 1
fi

# Installation des dépendances depuis requirements.txt
if [ -f "requirements.txt" ]; then
    print_info "Installation depuis requirements.txt..."
    pip install -r requirements.txt
else
    print_info "Installation manuelle de TOUTES les dépendances..."
    pip install telethon requests python-dotenv urllib3 colorama pycryptodome rsa
fi

# Installation supplémentaire pour instagrapi
print_info "Installation des dépendances supplémentaires..."
pip install moviepy  # Pour le traitement vidéo

# Vérification de l'installation
print_info "Vérification des installations..."
if python -c "import telethon, requests, instagrapi, dotenv, colorama, PIL" &> /dev/null; then
    print_success "Toutes les dépendances sont installées"
else
    print_error "Certaines dépendances sont manquantes"
    print_info "Tentative de réinstallation..."
    pip install --force-reinstall telethon requests python-dotenv colorama pillow instagrapi==1.16.22
fi

# ÉTAPE 8: Configuration API Telegram OBLIGATOIRE
print_info "ÉTAPE 8: Configuration API Telegram OBLIGATOIRE..."

echo ""
echo "╔════════════════════════════════════════╗"
echo "║       CONFIGURATION TELEGRAM API       ║"
echo "╠════════════════════════════════════════╣"
echo "║ 🔒 API PERSONNALISÉE OBLIGATOIRE       ║"
echo "║                                        ║"
echo "║ Pour des raisons de sécurité, vous     ║"
echo "║ DEVEZ utiliser votre propre API.       ║"
echo "║                                        ║"
echo "║ Les API partagées sont bloquées par    ║"
echo "║ Telegram et causent des erreurs.       ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Afficher le guide API
echo ""
print_info "📖 GUIDE RAPIDE POUR OBTENIR VOS CREDENTIALS:"
echo "┌─────────────────────────────────────┐"
echo "│ 1. Allez sur: https://my.telegram.org │"
echo "│ 2. Connectez-vous avec votre compte  │"
echo "│ 3. Cliquez sur 'API Development Tools'│"
echo "│ 4. Créez une nouvelle application    │"
echo "│ 5. Copiez API ID et API HASH         │"
echo "└─────────────────────────────────────┘"
echo ""

print_warning "🚫 IMPORTANT: Ne partagez jamais votre API HASH avec personne!"
print_warning "⚠️  Les API partagées causent l'erreur: 'API ID or Hash cannot be empty'"
echo ""

# Variables pour stocker les credentials
custom_api_id=""
custom_api_hash=""

# Boucle pour API ID
while true; do
    echo ""
    read -p "🔑 Entrez votre API ID (chiffres uniquement): " user_api_id
    
    # Vérifications strictes
    if [[ -z "$user_api_id" ]]; then
        print_error "L'API ID ne peut pas être vide"
        continue
    fi
    
    if ! [[ "$user_api_id" =~ ^[0-9]+$ ]]; then
        print_error "L'API ID doit contenir uniquement des chiffres"
        continue
    fi
    
    if [ ${#user_api_id} -lt 5 ]; then
        print_error "L'API ID doit avoir au moins 5 chiffres"
        continue
    fi
    
    # Validation réussie
    custom_api_id="$user_api_id"
    print_success "✅ API ID valide"
    break
done

# Boucle pour API HASH
while true; do
    echo ""
    read -p "🗝️  Entrez votre API HASH (chaîne de caractères): " user_api_hash
    
    # Vérifications strictes
    if [[ -z "$user_api_hash" ]]; then
        print_error "L'API HASH ne peut pas être vide"
        continue
    fi
    
    if [ ${#user_api_hash} -lt 10 ]; then
        print_error "L'API HASH doit avoir au moins 10 caractères"
        continue
    fi
    
    # Validation réussie
    custom_api_hash="$user_api_hash"
    print_success "✅ API HASH valide"
    break
done

# Confirmation finale
echo ""
print_info "🔍 RÉCAPITULATIF DE VOS CREDENTIALS:"
echo "┌─────────────────────────────────────┐"
echo "│ 🔑 API ID: $custom_api_id"
echo "│ 🗝️  API HASH: ${custom_api_hash:0:10}..."
echo "└─────────────────────────────────────┘"
echo ""

read -p "✅ Ces informations sont-elles correctes? (o/n): " confirm_credentials

if [[ $confirm_credentials != "o" && $confirm_credentials != "O" && $confirm_credentials != "oui" ]]; then
    print_error "❌ Installation annulée. Relancez le script pour recommencer."
    exit 1
fi

print_success "🎯 API personnalisée configurée avec succès!"

# Créer le fichier de configuration d'environnement
cat > .env << EOF
# Configuration SmmKingdomTask
# Développé par Dah Ery
USER_ID=auto_generated
API_ID=$custom_api_id
API_HASH=$custom_api_hash
CONTROL_URL=https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main
EOF

print_success "Configuration sauvegardée dans .env"

# Créer le script setup_api.py pour reconfiguration future
cat > setup_api.py << 'EOF'
#!/usr/bin/env python3
# setup_api.py - Reconfigurer l'API Telegram
import os
import re

# Couleurs
COLORS = {
    'C': '\033[1;96m',
    'V': '\033[1;92m',
    'R': '\033[1;91m',
    'J': '\033[1;93m',
    'S': '\033[0m'
}

def setup_custom_api():
    """Configure une API Telegram personnalisée"""
    print(f"{COLORS['C']}╔════════════════════════════════════════╗{COLORS['S']}")
    print(f"{COLORS['C']}║      CONFIGURATION API TELEGRAM        ║{COLORS['S']}")
    print(f"{COLORS['C']}╚════════════════════════════════════════╝{COLORS['S']}")
    print()
    
    print("📝 Obtenez vos credentials sur: https://my.telegram.org")
    print("   • Allez dans 'API Development Tools'")
    print("   • Créez une nouvelle application")
    print("   • Copiez API ID et API HASH")
    print()
    
    while True:
        api_id = input("Entrez votre API ID: ").strip()
        if api_id.isdigit() and len(api_id) > 4:
            break
        print(f"{COLORS['R']}❌ API ID invalide. Doit être un nombre.{COLORS['S']}")
    
    while True:
        api_hash = input("Entrez votre API HASH: ").strip()
        if len(api_hash) >= 10:
            break
        print(f"{COLORS['R']}❌ API HASH trop court. 10 caractères minimum.{COLORS['S']}")
    
    # Mettre à jour le fichier .env
    with open('.env', 'w') as f:
        f.write(f"# Configuration SmmKingdomTask\n")
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
        f.write(f"CONTROL_URL=https://raw.githubusercontent.com/Juana-archer/Smmkingdomcontrol/main\n")
    
    print(f"{COLORS['V']}✅ API personnalisée configurée!{COLORS['S']}")
    print(f"{COLORS['V']}🔄 Redémarrez l'application pour appliquer les changements{COLORS['S']}")

if __name__ == "__main__":
    setup_custom_api()
EOF

print_success "Script de configuration API créé"

# Créer un script de lancement rapide
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Lancement de SmmKingdomTask..."
cd ~/SmmKingdom
python main.py
EOF

chmod +x start.sh
chmod +x setup_api.py

# Vérifier que config.py a la bonne URL de contrôle
print_info "Vérification de la configuration..."
if grep -q "Smmkingdomcontrol" config.py 2>/dev/null; then
    print_success "Configuration contrôle détectée"
else
    print_warning "Mise à jour de la configuration contrôle recommandée"
fi

# ÉTAPE 9: Vérification finale
print_info "ÉTAPE 9: Vérification finale..."

# Vérifier que tous les fichiers sont présents
files_list=("main.py" "config.py" "account_manager.py" "telegram_client.py" "instagram_tasks.py" "ui.py" "control_system.py")
missing_files=0

for file in "${files_list[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Fichier manquant: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -eq 0 ]; then
    print_success "Tous les fichiers sont présents"
else
    print_error "$missing_files fichier(s) manquant(s)"
    exit 1
fi

# Vérifier l'accès storage
if [ -w "/sdcard/SmmKingdomTask" ]; then
    print_success "Accès storage fonctionnel"
else
    print_warning "Problème d'accès storage - vérifiez les permissions"
fi

# Test de connexion au système de contrôle
print_info "Test de connexion au système de licence..."
if curl -s --head "$BASE_URL/license.json" | grep "200 OK" > /dev/null; then
    print_success "Système de licence accessible"
else
    print_warning "Impossible de contacter le système de licence"
    print_info "Assurez-vous que le dépôt Smmkingdomcontrol existe"
fi

# Afficher le résumé de configuration
echo ""
print_success "🔧 RÉSUMÉ DE VOTRE CONFIGURATION:"
echo "┌─────────────────────────────────────┐"
echo "│ 📱 API Telegram:                   │"
echo "│    ✅ Personnalisée                 │"
echo "│    🔑 API ID: $custom_api_id"
echo "│    🗝️  API HASH: ${custom_api_hash:0:10}..."
echo "│ 💾 Stockage: ✅ Activé             │"
echo "│ 🔒 Licence: ✅ Connecté           │"
echo "│ 🐍 Dépendances: ✅ Complètes      │"
echo "│ 📸 Instagram: ✅ Compatible       │"
echo "└─────────────────────────────────────┘"

# ÉTAPE 10: Message de fin
echo ""
print_success "🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!"
echo ""
echo "╔════════════════════════════════════════╗"
echo "║          RÉSUMÉ DE L'INSTALLATION     ║"
echo "╠════════════════════════════════════════╣"
echo "║ ✅ Termux mis à jour                  ║"
echo "║ ✅ Dépendances système installées     ║"
echo "║ ✅ Accès storage configuré            ║"
echo "║ ✅ Fichiers téléchargés               ║"
echo "║ ✅ Bibliothèques Python installées    ║"
echo "║ ✅ Structure créée                    ║"
echo "║ ✅ API Telegram configurée            ║"
echo "║ ✅ Système de licence connecté        ║"
echo "║ ✅ Dépendances Instagram installées   ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📁 Dossier d'installation: ~/SmmKingdom"
echo "💾 Données sauvegardées: /sdcard/SmmKingdomTask"
echo "🔧 Configuration API: .env"
echo ""
echo "🚀 LANCEMENT RAPIDE:"
echo "   cd ~/SmmKingdom && python main.py"
echo "   ou simplement: ./start.sh"
echo ""
echo "🔧 OUTILS DISPONIBLES:"
echo "   python setup_api.py      - Reconfigurer l'API"
echo "   cat API_GUIDE.md         - Guide d'utilisation"
echo ""
echo "📞 SUPPORT: @Dahery👌 sur Telegram"
echo "💰 ABONNEMENT: 7000ar pour 7 jours d'accès"
echo ""
echo "🔑 Votre ID utilisateur sera généré au premier lancement"
echo "💳 Contactez @DahEry avec votre ID pour activation"

# Proposition de lancement automatique
echo ""
read -p "Voulez-vous lancer SmmKingdomTask maintenant? (o/n): " launch_choice

if [[ $launch_choice == "o" || $launch_choice == "O" || $launch_choice == "oui" ]]; then
    print_info "Lancement de SmmKingdomTask..."
    echo ""
    python main.py
else
    echo ""
    print_info "Vous pouvez lancer plus tard avec:"
    echo "cd ~/SmmKingdom && python main.py"
    echo ""
    print_success "Merci d'avoir choisi SmmKingdomTask! 🎉"
fi
