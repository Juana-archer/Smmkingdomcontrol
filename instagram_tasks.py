import time
import random
import re
import requests
import json
from account_manager import AccountManager

# ✅ CONFIGURATION DE SÉCURITÉ
SECURITY_CONFIG = {
    'daily_limits': {
        'likes': 80,
        'follows': 40,
        'comments': 15,
        'unfollows': 40,
        'total_actions': 150
    },
    'delays': {
        'like': (6, 15),
        'follow': (10, 25),
        'comment': (15, 30),
        'story': (8, 20),
        'between_sessions': (300, 600)
    }
}

# ✅ COMPTEURS ET SESSIONS
action_counters = {}
problem_accounts = {}
active_requests_sessions = {}

# ✅ FONCTIONS DE BASE
def check_daily_limits(username, action_type):
    """Vérifie les limites quotidiennes"""
    if username not in action_counters:
        return True

    counter = action_counters[username]
    daily_limits = SECURITY_CONFIG['daily_limits']

    if counter.get(action_type, 0) >= daily_limits.get(action_type, 50):
        print(f"⏸️ Limite {action_type} atteinte pour {username}")
        return False

    total_actions = sum([counter.get(action, 0) for action in ['likes', 'follows', 'comments', 'unfollows']])
    if total_actions >= daily_limits['total_actions']:
        print(f"⏸️ Limite quotidienne totale atteinte pour {username}")
        return False

    return True

def update_action_counter(username, action_type):
    """Met à jour le compteur d'actions"""
    if username in action_counters:
        action_counters[username][action_type] = action_counters[username].get(action_type, 0) + 1
        action_counters[username]['last_action'] = time.time()

def is_account_suspended(username):
    """Vérifie si un compte est suspendu"""
    if username in problem_accounts:
        suspension = problem_accounts[username]
        if time.time() - suspension.get('timestamp', 0) > 86400:
            del problem_accounts[username]
            return False
        return True
    return False

def mark_account_suspended(username, reason):
    """Marque un compte comme suspendu"""
    problem_accounts[username] = {
        'suspended': True,
        'reason': reason,
        'timestamp': time.time()
    }
    print(f"🚫 Compte {username} suspendu: {reason}")

def clean_instagram_url(url):
    """Nettoie les URLs Instagram"""
    if not url:
        return None

    url = re.sub(r'[\[\]\(\)<>]', '', url)
    url = url.replace(' ', '')

    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    matches = re.findall(url_pattern, url)

    if matches:
        url = matches[0]

    if 'instagram.com' not in url:
        return None

    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif not url.startswith('https://'):
        url = 'https://' + url

    url = url.split('?')[0]
    return url

# ✅ FONCTION PRINCIPALE POUR RÉCUPÉRER LES SESSIONS
def get_requests_session_for_tasks(username):
    """Récupère une session requests pour les tâches"""
    if is_account_suspended(username):
        return None

    # Essayer d'abord la session en mémoire
    session = active_requests_sessions.get(username)
    if session:
        try:
            # Tester la session
            test_response = session.get('https://www.instagram.com/api/v1/feed/timeline/', timeout=10)
            if test_response.status_code == 200:
                return session
        except:
            del active_requests_sessions[username]

    # Utiliser AccountManager pour obtenir une session requests
    manager = AccountManager()
    session = manager.get_requests_session_for_tasks(username)

    if session:
        active_requests_sessions[username] = session
        if username not in action_counters:
            action_counters[username] = {
                'likes': 0, 'follows': 0, 'comments': 0,
                'unfollows': 0, 'last_action': time.time()
            }
        print(f"✅ Session requests chargée pour {username}")

    return session

# ✅ FONCTION PRINCIPALE MODIFIÉE (utilise requests uniquement)
def execute_instagram_task(task_text, username):
    """Exécute une tâche Instagram avec REQUESTS uniquement"""
    try:
        if is_account_suspended(username):
            return False

        # 🎯 ANALYSE DE LA TÂCHE
        task_info = analyze_task_with_protection(task_text)
        if not task_info:
            print("❌ Tâche non reconnue")
            return False

        # ✅ Vérification limites avant action
        action_type = task_info['action'].lower()
        if 'like' in action_type and not check_daily_limits(username, 'likes'):
            return False
        elif 'follow' in action_type and not check_daily_limits(username, 'follows'):
            return False
        elif 'comment' in action_type and not check_daily_limits(username, 'comments'):
            return False

        # ⏳ Délai avant action
        human_delay()

        # 🔧 EXÉCUTION AVEC REQUESTS
        success = perform_action_with_requests(username, task_info)

        # ✅ Mise à jour compteur si succès
        if success:
            if 'like' in action_type:
                update_action_counter(username, 'likes')
            elif 'follow' in action_type:
                update_action_counter(username, 'follows')
            elif 'comment' in action_type:
                update_action_counter(username, 'comments')

        return success

    except Exception as e:
        print(f"❌ Erreur tâche avec requests: {e}")
        return False

# ✅ FONCTION D'EXÉCUTION AVEC REQUESTS
def perform_action_with_requests(username, task_info):
    """Exécute l'action avec requests uniquement"""
    action = task_info['action'].lower()
    link = task_info['link']

    try:
        clean_link = clean_instagram_url(link)
        if not clean_link:
            return False

        # Récupérer session requests
        session = get_requests_session_for_tasks(username)
        if not session:
            print(f"❌ Impossible d'obtenir session pour {username}")
            return False

        if 'like' in action:
            result = perform_like_with_requests(session, clean_link, username)
        elif 'follow' in action:
            result = perform_follow_with_requests(session, clean_link, username)
        elif 'comment' in action:
            result = perform_comment_with_requests(session, clean_link, username)
        elif 'story' in action or 'video' in action:
            result = perform_watch_with_requests(session, clean_link, username)
        else:
            print(f"❌ Action non supportée: {action}")
            return False

        if not result:
            mark_account_suspended(username, f"Échec action: {action}")

        return result

    except Exception as e:
        print(f"❌ Erreur action avec requests: {e}")
        mark_account_suspended(username, f"Exception: {str(e)}")
        return False

# ✅ FONCTIONS D'ACTION AVEC REQUESTS - CORRIGÉES
def perform_like_with_requests(session, link, username):
    """Like avec requests - VERSION CORRIGÉE"""
    try:
        print(f"❤️ Tentative de like pour {username}")
        
        # Nettoyer les cookies avant l'action
        from account_manager import AccountManager
        manager = AccountManager()
        manager.clean_duplicate_cookies(session)
        
        # Extraire l'ID média du lien
        media_id = extract_media_id_from_url(link)
        if not media_id:
            print("❌ Impossible d'extraire l'ID média")
            return False

        # Délai avant action
        time.sleep(random.uniform(3, 8))

        # Endpoint pour like
        like_url = f"https://www.instagram.com/api/v1/web/likes/{media_id}/like/"
        
        # Récupérer le CSRF token des cookies nettoyés
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("❌ CSRF token manquant")
            return False
            
        # Headers pour la requête API
        headers = {
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
            'Referer': 'https://www.instagram.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = session.post(like_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Like réussi pour {username}")
            time.sleep(random.uniform(2, 5))
            return True
        else:
            print(f"❌ Échec like (status: {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Erreur like avec requests: {e}")
        return False

def perform_follow_with_requests(session, link, username):
    """Follow avec requests - VERSION CORRIGÉE"""
    try:
        print(f"👤 Tentative de follow pour {username}")
        
        # Nettoyer les cookies avant l'action
        from account_manager import AccountManager
        manager = AccountManager()
        manager.clean_duplicate_cookies(session)
        
        # Extraire le username du profil
        target_username = extract_username_from_url(link)
        if not target_username:
            print("❌ Impossible d'extraire le username")
            return False

        # Délai avant action
        time.sleep(random.uniform(8, 15))

        # Récupérer l'user_id du target
        user_id = get_user_id_from_username(session, target_username)
        if not user_id:
            print("❌ Impossible de récupérer l'user_id")
            return False

        # Endpoint pour follow
        follow_url = f"https://www.instagram.com/api/v1/friendships/create/{user_id}/follow/"
        
        # Récupérer le CSRF token des cookies nettoyés
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("❌ CSRF token manquant")
            return False
            
        headers = {
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
            'Referer': f'https://www.instagram.com/{target_username}/',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = session.post(follow_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Follow réussi pour {username}")
            time.sleep(random.uniform(10, 20))
            return True
        else:
            print(f"❌ Échec follow (status: {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Erreur follow avec requests: {e}")
        return False

def perform_comment_with_requests(session, link, username):
    """Commentaire avec requests - VERSION CORRIGÉE"""
    try:
        print(f"💬 Tentative de commentaire pour {username}")
        
        # Nettoyer les cookies avant l'action
        from account_manager import AccountManager
        manager = AccountManager()
        manager.clean_duplicate_cookies(session)
        
        media_id = extract_media_id_from_url(link)
        if not media_id:
            return False

        time.sleep(random.uniform(15, 25))

        # Commentaire simple
        comments = [
            "Nice! 👍",
            "Great post! 👏", 
            "Awesome! 😊",
            "Love this! ❤️",
            "So cool! 🔥"
        ]
        comment_text = random.choice(comments)

        comment_url = f"https://www.instagram.com/api/v1/web/comments/{media_id}/add/"
        
        # Récupérer le CSRF token des cookies nettoyés
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print("❌ CSRF token manquant")
            return False
            
        headers = {
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
            'Referer': link,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'comment_text': comment_text,
            'replied_to_comment_id': ''
        }

        response = session.post(comment_url, data=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Commentaire réussi pour {username}")
            time.sleep(random.uniform(20, 30))
            return True
        else:
            print(f"❌ Échec commentaire (status: {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Erreur commentaire avec requests: {e}")
        return False

def perform_watch_with_requests(session, link, username):
    """Watch story/video avec requests"""
    try:
        print(f"📹 Tentative de watch pour {username}")
        
        time.sleep(random.uniform(5, 12))

        # Simuler le visionnage
        if '/stories/' in link:
            print(f"📖 Visualisation story pour {username}")
            time.sleep(random.uniform(10, 20))
        elif '/reel/' in link or 'video' in link.lower():
            print(f"🎥 Visualisation video pour {username}")
            time.sleep(random.uniform(15, 25))

        time.sleep(random.uniform(3, 7))
        print(f"✅ Watch réussi pour {username}")
        return True

    except Exception as e:
        print(f"❌ Erreur watch avec requests: {e}")
        return False

# ✅ FONCTIONS UTILITAIRES POUR REQUESTS - CORRIGÉES
def extract_media_id_from_url(url):
    """Extrait l'ID média d'une URL Instagram"""
    try:
        patterns = [
            r'/p/([^/?]+)',
            r'/reel/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except:
        return None

def extract_username_from_url(url):
    """Extrait le username d'une URL de profil - VERSION CORRIGÉE"""
    try:
        # Nettoyer l'URL d'abord
        clean_url = clean_instagram_url(url)
        if not clean_url:
            return None
            
        # Patterns améliorés pour les URLs Instagram
        patterns = [
            r'instagram\.com/([a-zA-Z0-9_.]+)/?$',
            r'instagram\.com/([a-zA-Z0-9_.]+)\?',
            r'instagram\.com/([a-zA-Z0-9_.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_url)
            if match:
                username = match.group(1)
                # Filtrer les noms de pages spéciaux
                if username not in ['p', 'reel', 'stories', 'explore', 'accounts']:
                    return username
        return None
    except:
        return None

def get_user_id_from_username(session, username):
    """Récupère l'user_id depuis un username - VERSION CORRIGÉE"""
    try:
        profile_url = f"https://www.instagram.com/{username}/"
        
        # Headers améliorés
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        response = session.get(profile_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Recherche améliorée de l'user_id
            patterns = [
                r'"user_id":"(\d+)"',
                r'"profile_user_id":"(\d+)"',
                r'instagram://user\?id=(\d+)',
                r'content="instagram://user\?id=(\d+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
                    
        print(f"❌ User ID non trouvé pour {username} (status: {response.status_code})")
        return None
        
    except Exception as e:
        print(f"❌ Erreur récupération user_id: {e}")
        return None

# ✅ FONCTIONS EXISTANTES CONSERVÉES
def analyze_task_with_protection(task_text):
    """Analyse la tâche avec détection avancée"""
    if not task_text:
        return None

    task_info = {
        'type': 'Unknown',
        'link': '',
        'action': '',
        'reward': '',
        'risk_level': 'low'
    }

    text_lower = task_text.lower()
    if 'follow' in text_lower:
        task_info['risk_level'] = 'medium'
    elif 'comment' in text_lower:
        task_info['risk_level'] = 'high'

    action_patterns = {
        'like the post': 'Like the post',
        'follow the profile': 'Follow the profile', 
        'comment on post': 'Comment on post',
        'watch the story': 'Watch the story',
        'watch the video': 'Watch the video',
        'open the video': 'Watch the video'
    }

    for pattern, action_name in action_patterns.items():
        if pattern in text_lower:
            task_info['action'] = action_name
            task_info['type'] = action_name
            break

    link_patterns = [
        r'https?://(?:www\.)?instagram\.com/p/[^\s]+',
        r'https?://(?:www\.)?instagram\.com/reel/[^\s]+',
        r'https?://(?:www\.)?instagram\.com/stories/[^\s]+',
        r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+/?(?:\?[^\s]*)?',
        r'link\s*:\s*(https?://[^\s]+)'
    ]

    for pattern in link_patterns:
        links = re.findall(pattern, task_text, re.IGNORECASE)
        if links:
            task_info['link'] = links[0].strip()
            break

    reward_match = re.search(r'reward\s*:\s*([0-9.]+)\s*cashcoins', text_lower)
    if reward_match:
        task_info['reward'] = f"{reward_match.group(1)} CashCoins"
    else:
        task_info['reward'] = 'CashCoins'

    return task_info if task_info['link'] else None

def human_delay():
    """Délai de comportement humain"""
    delay = random.uniform(2, 8)
    time.sleep(delay)

def get_action_stats(username):
    """Retourne les statistiques d'actions"""
    if username in action_counters:
        return action_counters[username]
    return None

def reset_problem_account(username):
    """Réinitialise un compte problématique"""
    if username in problem_accounts:
        del problem_accounts[username]
        print(f"✅ Compte {username} réinitialisé")
        return True
    return False

def reset_daily_counters():
    """Réinitialise les compteurs quotidiens"""
    global action_counters
    for username in action_counters:
        action_counters[username] = {
            'likes': 0, 'follows': 0, 'comments': 0,
            'unfollows': 0, 'last_action': time.time()
        }
    print("✅ Compteurs quotidiens réinitialisés")

def get_problem_accounts():
    """Retourne les comptes avec problèmes"""
    manager = AccountManager()
    problem_accounts_dict = {}

    for username, data in manager.accounts.items():
        if data.get('status') == 'problem':
            problem_accounts_dict[username] = {
                'reason': data.get('last_error', 'Raison inconnue'),
                'error_time': data.get('error_time', '')
            }

    return problem_accounts_dict

def clean_corrupted_sessions():
    """Nettoie les sessions corrompues"""
    manager = AccountManager()
    cleaned_count = 0

    for username, data in manager.accounts.items():
        if not manager.validate_session(username) and data.get('session_data'):
            data['session_data'] = ''
            data['cookies'] = ''
            data['status'] = 'needs_login'
            cleaned_count += 1

    if cleaned_count > 0:
        manager.save_accounts()
        print(f"🧹 {cleaned_count} session(s) corrompue(s) nettoyée(s)")

    return cleaned_count
