#!/data/data/com.termux/files/usr/bin/bash
# install.sh - Script d'installation par Dah Ery

echo ""
echo "┌────────────────────────────────────────────────┐"
echo "│            🚀 SMM KINGDOM TASK V3.0            │"
echo "│              👑 Contrôlé par Dah Ery           │"
echo "└────────────────────────────────────────────────┘"
echo ""

# Couleurs
RED='\033[1;91m'
GREEN='\033[1;92m'
YELLOW='\033[1;93m'
CYAN='\033[1;96m'
NC='\033[0m'

# Fonctions
log() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${CYAN}[ℹ]${NC} $1"; }

# Vérification Termux
if [ ! -d "/data/data/com.termux/files/usr" ]; then
    error "Ce script doit être exécuté dans Termux"
    exit 1
fi

echo ""
info "Début de l'installation..."
echo ""

# Mise à jour
log "Mise à jour de Termux..."
pkg update -y && pkg upgrade -y

# Installation dépendances
log "Installation de Python..."
pkg install -y python git

log "Installation des modules Python..."
pip install telethon requests beautifulsoup4 instagrapi

# Accès stockage
log "Demande d'accès au stockage..."
termux-setup-storage
sleep 2

# Création dossier
log "Création du dossier..."
cd ~
mkdir -p SmmKingdom
cd SmmKingdom

# Téléchargement fichiers
log "Téléchargement des fichiers..."

# Liste des fichiers à télécharger
files=("main.py" "config.py" "control_system.py" "account_manager.py" "telegram_client.py" "ui.py" "instagram_tasks.py")

for file in "${files[@]}"; do
    url="https://raw.githubusercontent.com/Juana-archa/SmmKingdomControl/main/$file"
    if curl -s -o "$file" "$url"; then
        log "Téléchargé: $file"
    else
        error "Échec: $file"
    fi
done

# Permissions
log "Configuration des permissions..."
chmod +x main.py

# Dossiers données
log "Création des dossiers de données..."
mkdir -p /sdcard/SmmKingdomTask

echo ""
echo "================================================"
info "✅ INSTALLATION TERMINÉE AVEC SUCCÈS!"
echo "================================================"
echo ""
echo "📋 INSTRUCTIONS D'UTILISATION:"
echo "1. cd ~/SmmKingdom"
echo "2. python main.py"
echo ""
echo "📞 CONTACT DAH ERY POUR ACTIVATION:"
echo "WhatsApp: +261385873519 "
echo "Facebook: Dah Ery"
echo ""
