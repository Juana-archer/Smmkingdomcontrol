# instagram_tasks.py - VERSION ULTIME AVEC GESTION DES CODES
import time
import random
import re
import os
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, ChallengeRequired, PleaseWaitFewMinutes

# Dossier pour stocker les sessions
SESSIONS_DIR = "instagram_sessions"

# Comptes problématiques
problem_accounts = {}

def ensure_sessions_dir():
    """Crée le dossier des sessions s'il n'existe pas"""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)

def clean_instagram_url(url):
    """Nettoie les URLs Instagram - VERSION AMÉLIORÉE"""
    if not url:
        return url

    # Méthode SIMPLE et FIABLE : prendre seulement la partie avant le premier ] ou (
    if ']' in url:
        url = url.split(']')[0]
    if '(' in url:
        url = url.split('(')[0]

    # Supprimer les caractères parasites restants
    url = re.sub(r'[\[\]\(\)]', '', url)
    url = url.replace(' ', '')

    # Vérifier que c'est une URL Instagram valide
    if 'instagram.com' not in url:
        return None

    # Forcer https
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif not url.startswith('https://'):
        url = 'https://' + url

    return url

def is_account_suspended(username):
    """Vérifie si un compte est marqué comme suspendu"""
    return problem_accounts.get(username, {}).get('suspended', False)

def mark_account_suspended(username, reason):
    """Marque un compte comme suspendu"""
    problem_accounts[username] = {
        'suspended': True,
        'reason': reason,
        'timestamp': time.time()
    }
    print(f"🚫 Compte {username} suspendu: {reason}")

# AJOUT DE LA FONCTION MANQUANTE
def check_single_account_status(username):
    """Vérifie le statut d'un compte spécifique - POUR LE MENU"""

    # Vérifier d'abord si déjà marqué suspendu
    if is_account_suspended(username):
        return "suspended"

    from account_manager import AccountManager
    account_manager = AccountManager()
    account_data = account_manager.accounts.get(username, {})

    if not account_data:
        return "unknown"

    password = account_data.get('password')
    if not password:
        return "unknown"

    session_file = os.path.join(SESSIONS_DIR, f"{username}.json")

    # Si le fichier de session existe, le compte a déjà fonctionné
    if os.path.exists(session_file):
        try:
            client = Client()
            client.load_settings(session_file)
            # Test rapide
            client.get_timeline_feed()
            return "working"
        except:
            return "verification"

    # Si pas de session, on essaie une connexion simple
    try:
        client = Client()
        client.delay_range = [1, 2]
        client.login(username, password)
        client.dump_settings(session_file)
        return "working"
    except ChallengeRequired:
        return "verification"
    except PleaseWaitFewMinutes:
        mark_account_suspended(username, "Trop de tentatives - Attendre")
        return "suspended"
    except Exception as e:
        error_msg = str(e).lower()
        if any(word in error_msg for word in ['checkpoint', 'suspended', 'disabled', 'wait', 'login']):
            mark_account_suspended(username, "Problème de connexion")
            return "suspended"
        return "unknown"

def execute_instagram_task(task_text, cookies_str, username):
    """Exécute la tâche Instagram - VERSION SIMPLIFIÉE"""

    # Vérifier si le compte est suspendu
    if is_account_suspended(username):
        return False

    try:
        # Analyser la tâche
        task_info = analyze_instagram_task(task_text)
        if not task_info:
            return False

        task_type = task_info['type']
        target_url = task_info['link']

        # Récupérer le client Instagram
        client = get_instagram_client(username)
        if not client:
            return False

        # Exécuter l'action
        if 'like' in task_type.lower():
            success = like_instagram_post(target_url, client, username)
        elif 'follow' in task_type.lower():
            success = follow_instagram_profile(target_url, client, username)
        elif 'comment' in task_type.lower():
            success = comment_instagram_post(target_url, client, username)
        elif 'story' in task_type.lower():
            success = watch_instagram_story(target_url, client, username)
        elif 'video' in task_type.lower():
            success = watch_instagram_video(target_url, client, username)
        else:
            return False

        if success:
            print("✅ Action réussie")
            time.sleep(random.uniform(2, 3))
            return True
        else:
            return False

    except Exception:
        return False

def get_instagram_client(username):
    """Récupère un client Instagram - VERSION ULTRA-SIMPLE"""
    ensure_sessions_dir()

    if is_account_suspended(username):
        return None

    from account_manager import AccountManager
    account_manager = AccountManager()
    account_data = account_manager.accounts.get(username, {})

    if not account_data:
        return None

    password = account_data.get('password')
    if not password:
        return None

    session_file = os.path.join(SESSIONS_DIR, f"{username}.json")
    client = Client()

    # Configuration minimale
    client.delay_range = [1, 2]

    try:
        # Gestion très simple des sessions
        if os.path.exists(session_file):
            try:
                client.load_settings(session_file)
                # Test rapide de la session
                client.get_timeline_feed()
            except:
                # Si session invalide, nouvelle connexion
                client.login(username, password)
        else:
            # Nouvelle connexion
            client.login(username, password)

        # Sauvegarder la session
        client.dump_settings(session_file)
        return client

    except ChallengeRequired:
        print(f"📧 {username} demande une vérification par email")
        try:
            # Essayer de résoudre le challenge automatiquement
            client.challenge_resolve(client.last_json)
            client.dump_settings(session_file)
            return client
        except:
            mark_account_suspended(username, "Vérification manuelle requise")
            return None

    except PleaseWaitFewMinutes:
        mark_account_suspended(username, "Trop de tentatives - Attendre")
        return None

    except Exception as e:
        error_msg = str(e).lower()
        if any(word in error_msg for word in ['checkpoint', 'suspended', 'disabled', 'wait', 'login']):
            mark_account_suspended(username, "Problème de compte")
        return None

def analyze_instagram_task(text):
    """Analyse la tâche Instagram - VERSION FIABLE"""
    if not text:
        return None

    task_info = {'type': 'Unknown', 'link': ''}
    text_lower = text.lower()

    # Détection du type de tâche
    if 'like the post' in text_lower:
        task_info['type'] = 'Like the post'
    elif 'follow the profile' in text_lower:
        task_info['type'] = 'Follow the profile'
    elif 'comment on post' in text_lower:
        task_info['type'] = 'Comment on post'
    elif 'watch the story' in text_lower:
        task_info['type'] = 'Watch story'
    elif 'watch the video' in text_lower:
        task_info['type'] = 'Watch video'

    # Méthode SIMPLE pour extraire l'URL : prendre le premier lien Instagram
    url_pattern = r'https?://[^\s\]\[]+instagram\.com[^\s\]\[]*'
    links = re.findall(url_pattern, text, re.IGNORECASE)

    if links:
        cleaned_url = clean_instagram_url(links[0])
        if cleaned_url:
            task_info['link'] = cleaned_url

    return task_info if task_info['link'] else None

def extract_media_id_from_url(url):
    """Extrait l'ID média depuis l'URL"""
    try:
        pattern = r'instagram\.com/(?:p|reel)/([^/?]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    except:
        return None

def extract_username_from_url(url):
    """Extrait le username depuis l'URL"""
    try:
        pattern = r'instagram\.com/([^/?]+)'
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            if username not in ['p', 'reel', 'stories', 'explore', 'accounts', 'direct']:
                return username
        return None
    except:
        return None

def like_instagram_post(post_url, client, username):
    """Like un post Instagram - VERSION ROBUSTE"""
    try:
        # Nettoyer l'URL
        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        # Extraire l'ID média
        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        # Petit délai
        time.sleep(random.uniform(1, 2))

        # Récupérer l'ID média
        media_id = client.media_id(media_code)
        if not media_id:
            return False

        # Like
        result = client.media_like(media_id)

        return bool(result)

    except Exception:
        return False

def follow_instagram_profile(profile_url, client, username):
    """Follow un profil Instagram - VERSION ROBUSTE"""
    try:
        clean_url = clean_instagram_url(profile_url)
        if not clean_url:
            return False

        target_username = extract_username_from_url(clean_url)
        if not target_username:
            return False

        time.sleep(random.uniform(2, 3))

        user_id = client.user_id_from_username(target_username)
        if not user_id:
            return False

        result = client.user_follow(user_id)
        return bool(result)

    except Exception:
        return False

def comment_instagram_post(post_url, client, username):
    """Commenter un post Instagram"""
    try:
        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        time.sleep(random.uniform(2, 3))

        media_id = client.media_id(media_code)
        if not media_id:
            return False

        comments = ["Nice!", "Great post!", "Awesome  👍", "Love it ❤️"]
        comment_text = random.choice(comments)

        result = client.media_comment(media_id, comment_text)
        return bool(result)

    except Exception:
        return False

def watch_instagram_story(story_url, client, username):
    """Regarder une story Instagram"""
    try:
        clean_url = clean_instagram_url(story_url)
        if not clean_url:
            return False

        story_username = extract_username_from_url(clean_url)
        if not story_username:
            return False

        time.sleep(random.uniform(1, 2))

        user_id = client.user_id_from_username(story_username)
        stories = client.user_stories(user_id)

        if not stories:
            return False

        story_id = stories[0].id
        result = client.story_seen([story_id])

        time.sleep(random.uniform(4, 6))

        return bool(result)

    except Exception:
        return False

def watch_instagram_video(video_url, client, username):
    """Regarder une vidéo Instagram"""
    try:
        clean_url = clean_instagram_url(video_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        time.sleep(random.uniform(1, 2))

        media_info = client.media_info(media_code)

        time.sleep(random.uniform(6, 8))

        return bool(media_info)

    except Exception:
        return False

def get_problem_accounts():
    """Retourne les comptes problématiques"""
    return problem_accounts

def reset_all_accounts():
    """Réinitialise tous les comptes (pour redémarrer)"""
    global problem_accounts
    problem_accounts = {}
    # Supprimer toutes les sessions
    if os.path.exists(SESSIONS_DIR):
        for file in os.listdir(SESSIONS_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(SESSIONS_DIR, file))

if __name__ == "__main__":
    # Test
    from account_manager import AccountManager
    manager = AccountManager()

    test_task = "Link: https://www.instagram.com/p/ABC123/ Action: Like the post Reward: 0.5 CashCoins"
    result = execute_instagram_task(test_task, "", "test_user")
    print(f"Résultat: {'✅ SUCCÈS' if result else '❌ ÉCHEC'}")
