#!/data/data/com.termux/files/usr/bin/bash
# install.sh - Version corrigée

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

log() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${CYAN}[ℹ]${NC} $1"; }

# Vérification Termux
[ ! -d "/data/data/com.termux/files/usr" ] && error "Exécutez dans Termux" && exit 1

echo "" && info "Début de l'installation..."

# Mise à jour
log "Mise à jour Termux..."
pkg update -y && pkg upgrade -y

# Dépendances
log "Installation Python..."
pkg install -y python git curl

log "Installation modules Python..."
pip install telethon requests beautifulsoup4 instagrapi

# 🔥 CORRECTION : Accès stockage AVANT création dossiers
log "Demande d'accès au stockage..."
termux-setup-storage

# 🔥 ATTENDRE que l'utilisateur accorde l'accès
warning "📱 ACCORDEZ L'ACCÈS AU STOCKAGE DANS LA POPUP!"
warning "⏳ Attente de la permission..."
sleep 10

# 🔥 VÉRIFIER si l'accès est accordé
if [ ! -d "/sdcard" ] || [ ! -w "/sdcard" ]; then
    error "❌ Accès stockage non accordé!"
    warning "📱 Veuillez accorder l'accès et relancer:"
    warning "termux-setup-storage"
    exit 1
fi

# Dossier application
log "Création dossier application..."
cd ~
rm -rf SmmKingdom 2>/dev/null
mkdir -p SmmKingdom
cd SmmKingdom

# 🔥 CORRECTION : Téléchargement robuste
log "Téléchargement fichiers..."

download_file() {
    local file=$1
    local url="https://raw.githubusercontent.com/Juana-archer/SmmKingdomControl/main/$file"
    
    # Essai multiple
    for i in {1..3}; do
        if curl -s -o "$file" "$url"; then
            log "Téléchargé: $file"
            return 0
        else
            warning "Essai $i échoué: $file"
            sleep 2
        fi
    done
    error "Échec: $file"
    return 1
}

# Fichiers essentiels
essential_files=("main.py" "config.py" "control_system.py")

for file in "${essential_files[@]}"; do
    if ! download_file "$file"; then
        error "❌ Fichier essentiel manquant!"
        exit 1
    fi
done

# Fichiers optionnels
optional_files=("account_manager.py" "telegram_client.py" "ui.py" "instagram_tasks.py")

for file in "${optional_files[@]}"; do
    download_file "$file"
done

# Permissions
log "Configuration permissions..."
chmod +x main.py

# 🔥 CORRECTION : Création dossier données avec vérification
log "Création dossiers données..."
if [ -w "/sdcard" ]; then
    mkdir -p /sdcard/SmmKingdomTask 2>/dev/null && log "Dossier créé: /sdcard/SmmKingdomTask"
else
    warning "⚠️  Création dossier local à la place..."
    mkdir -p ~/SmmKingdomData
    ln -sf ~/SmmKingdomData /sdcard/SmmKingdomTask 2>/dev/null || true
fi

echo ""
echo "================================================"
info "✅ INSTALLATION TERMINÉE!"
echo "================================================"
echo ""
echo "📋 INSTRUCTIONS D'UTILISATION:"
echo "1. cd ~/SmmKingdom"
echo "2. python main.py"
echo ""
echo "🔧 EN CAS DE PROBLÈME:"
echo "• Relancer: termux-setup-storage"
echo "• Vérifier connexion Internet"
echo ""
echo "📞 CONTACT DAH ERY POUR ACTIVATION:"
echo "💰 5€ pour 7 jours - 10€ pour 15 jours - 20€ pour 30 jours"
echo "📱 WhatsApp: +261385873519"
echo "👤 Facebook: Dah Ery"
echo ""
