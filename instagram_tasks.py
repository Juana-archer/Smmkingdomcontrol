# instagram_tasks.py - VERSION CORRIGÉE AVEC AFFICHAGE PROFESSIONNEL
import time
import random
import re
import os
import json
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, ChallengeRequired

# Gestion des comptes problématiques
problem_accounts = {}

def clean_corrupted_sessions():
    """Nettoie toutes les sessions corrompues"""
    try:
        from account_manager import AccountManager
        account_manager = AccountManager()

        for username in account_manager.accounts:
            account_manager.accounts[username]['cookies'] = ''

        account_manager.save_accounts()
        print("✅ Toutes les sessions ont été nettoyées")
        return True

    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")
        return False

def get_instagram_client(username):
    """
    VERSION AVEC AFFICHAGE PROFESSIONNEL
    """
    try:
        from account_manager import AccountManager

        account_manager = AccountManager()

        if username not in account_manager.accounts:
            return None

        account_data = account_manager.accounts[username]
        password = account_data.get('password')

        if not password:
            return None

        # Vérifier si le compte est suspendu
        if is_account_suspended(username):
            return None

        # Créer le client
        client = Client()
        client.delay_range = [2, 6]

        # Gestion des cookies
        cookies_str = account_data.get('cookies', '')

        if cookies_str:
            try:
                # Essayer de parser comme JSON d'abord
                try:
                    cookies_dict = json.loads(cookies_str)
                except:
                    # Fallback: format string original
                    cookies_dict = {}
                    for cookie in cookies_str.split('; '):
                        if '=' in cookie:
                            key, value = cookie.split('=', 1)
                            cookies_dict[key.strip()] = value.strip()

                client.set_cookies(cookies_dict)

                # Tester la session - MESSAGE PROFESSIONNEL
                client.get_timeline_feed()
                print(f"✔ Session restaurée pour {username}")
                return client

            except Exception as e:
                print(f"🔄 Session expirée pour {username}")

        # NOUVELLE AUTHENTIFICATION
        print(f"🔐 Authentification pour {username}...")
        try:
            client.login(username, password)

            # Sauvegarder les cookies
            new_cookies_dict = client.get_cookies()
            cookies_list = []
            for key, value in new_cookies_dict.items():
                cookies_list.append(f"{key}={value}")
            new_cookies_str = '; '.join(cookies_list)

            account_manager.accounts[username]['cookies'] = new_cookies_str
            account_manager.save_accounts()

            print(f"✔ Session créée pour {username}")
            time.sleep(3)
            return client

        except LoginRequired as e:
            print(f"❌ Login requis pour {username}")
            return None
        except ChallengeRequired as e:
            print(f"🛡️ Vérification sécurité requise pour {username}")
            return None
        except Exception as login_error:
            print(f"❌ Échec authentification pour {username}")
            return None

    except Exception as e:
        return None

def is_account_suspended(username):
    """Vérifie si un compte est suspendu"""
    return problem_accounts.get(username, {}).get('suspended', False)

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

    # Méthode simple et fiable
    if ']' in url:
        url = url.split(']')[0]
    if '(' in url:
        url = url.split('(')[0]

    # Supprimer les caractères parasites
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

def analyze_instagram_task(text):
    """Analyse la tâche Instagram avec extraction du texte de commentaire"""
    if not text:
        return None

    task_info = {'type': 'Unknown', 'link': '', 'comment_text': ''}
    text_lower = text.lower()

    # Détection du type de tâche
    if 'like the post' in text_lower or 'like' in text_lower:
        task_info['type'] = 'Like the post'
    elif 'follow the profile' in text_lower or 'follow' in text_lower:
        task_info['type'] = 'Follow the profile'
    elif 'comment on post' in text_lower or 'comment' in text_lower:
        task_info['type'] = 'Comment on post'

        # Extraire le texte du commentaire depuis la tâche
        comment_patterns = [
            r'comment on post:\s*([^\n]+?)\s*https?://',
            r'comment:\s*([^\n]+?)\s*https?://',
            r'comment\s*"([^"]+)"',
            r"comment\s*'([^']+)'",
        ]

        for pattern in comment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_info['comment_text'] = match.group(1).strip()
                break

        # Si pas trouvé avec les patterns, essayer une méthode simple
        if not task_info['comment_text']:
            url_match = re.search(r'https?://[^\s]+', text)
            if url_match:
                url_start = url_match.start()
                comment_part = text[:url_start].lower()
                if 'comment' in comment_part:
                    comment_start = comment_part.find('comment') + 7
                    task_info['comment_text'] = text[comment_start:url_start].strip(' :"\'()-')

    elif 'watch the story' in text_lower or 'story' in text_lower:
        task_info['type'] = 'Watch story'
    elif 'watch the video' in text_lower or 'video' in text_lower:
        task_info['type'] = 'Watch video'

    # Extraction URL
    url_pattern = r'https?://[^\s\]\[]+instagram\.com[^\s\]\[]*'
    links = re.findall(url_pattern, text, re.IGNORECASE)

    if links:
        cleaned_url = clean_instagram_url(links[0])
        if cleaned_url:
            task_info['link'] = cleaned_url

    return task_info if task_info['link'] else None

def human_delay(action_type):
    """Délai humain selon le type d'action"""
    delays = {
        'like': (3, 8),
        'follow': (5, 12),
        'comment': (8, 15),
        'story': (2, 6),
        'video': (10, 20)
    }

    min_delay, max_delay = delays.get(action_type, (2, 5))
    time.sleep(random.uniform(min_delay, max_delay))

def execute_instagram_task(task_text, username):
    """
    EXÉCUTE DE VRAIES ACTIONS INSTAGRAM - AFFICHAGE MINIMAL
    """
    # Récupérer le client
    client = get_instagram_client(username)
    if not client:
        return False

    # Analyser la tâche
    task_info = analyze_instagram_task(task_text)
    if not task_info:
        return False

    task_type = task_info['type']
    target_url = task_info['link']

    try:
        # Exécuter l'action avec gestion d'erreurs
        if 'like' in task_type.lower():
            return like_instagram_post(target_url, client, username)
        elif 'follow' in task_type.lower():
            return follow_instagram_profile(target_url, client, username)
        elif 'comment' in task_type.lower():
            comment_text = task_info.get('comment_text', '')
            if not comment_text:
                return False
            return comment_instagram_post(target_url, client, username, comment_text)
        elif 'story' in task_type.lower():
            return watch_instagram_story(target_url, client, username)
        elif 'video' in task_type.lower():
            return watch_instagram_video(target_url, client, username)
        else:
            return False

    except Exception as e:
        return False

def like_instagram_post(post_url, client, username):
    """Like RÉEL d'un post Instagram"""
    try:
        human_delay('like')

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        # Récupérer l'ID média
        media_id = client.media_id(media_code)
        if not media_id:
            return False

        # Vérifier si déjà liké
        try:
            media_info = client.media_info(media_id)
            if media_info.has_liked:
                return True
        except:
            pass

        # Effectuer le like
        result = client.media_like(media_id)

        if result:
            time.sleep(random.uniform(2, 4))
            return True
        else:
            return False

    except Exception as e:
        return False

def follow_instagram_profile(profile_url, client, username):
    """Follow RÉEL d'un profil Instagram"""
    try:
        human_delay('follow')

        clean_url = clean_instagram_url(profile_url)
        if not clean_url:
            return False

        target_username = extract_username_from_url(clean_url)
        if not target_username:
            return False

        # Récupérer l'ID utilisateur
        user_id = client.user_id_from_username(target_username)
        if not user_id:
            return False

        # Vérifier si déjà follow
        try:
            user_info = client.user_info(user_id)
            if user_info.following:
                return True
        except:
            pass

        # Effectuer le follow
        result = client.user_follow(user_id)

        if result:
            time.sleep(random.uniform(3, 6))
            return True
        else:
            return False

    except Exception as e:
        return False

def comment_instagram_post(post_url, client, username, comment_text=None):
    """Commentaire RÉEL sur un post Instagram avec texte personnalisé"""
    try:
        human_delay('comment')

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        media_id = client.media_id(media_code)
        if not media_id:
            return False

        # Vérifier si un texte de commentaire est fourni
        if not comment_text or comment_text.strip() == "":
            return False

        # Vérifier la longueur du commentaire
        if len(comment_text) > 300:
            comment_text = comment_text[:300] + "..."

        # Simuler la frappe humaine
        time.sleep(random.uniform(2, 4))

        # Poster le commentaire
        result = client.media_comment(media_id, comment_text)

        if result:
            time.sleep(random.uniform(4, 8))
            return True
        else:
            return False

    except Exception as e:
        return False

def watch_instagram_story(story_url, client, username):
    """Visionnage RÉEL d'une story Instagram"""
    try:
        human_delay('story')

        clean_url = clean_instagram_url(story_url)
        if not clean_url:
            return False

        story_username = extract_username_from_url(clean_url)
        if not story_username:
            return False

        # Récupérer l'ID utilisateur
        user_id = client.user_id_from_username(story_username)

        # Récupérer les stories
        stories = client.user_stories(user_id)
        if not stories:
            return False

        # Marquer la première story comme vue
        story_id = stories[0].id
        result = client.story_seen([story_id])

        if result:
            time.sleep(random.uniform(4, 6))
            return True
        else:
            return False

    except Exception as e:
        return False

def watch_instagram_video(video_url, client, username):
    """Visionnage RÉEL d'une vidéo Instagram"""
    try:
        human_delay('video')

        clean_url = clean_instagram_url(video_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        # Récupérer les infos de la vidéo (simule le visionnage)
        media_info = client.media_info(media_code)

        if media_info:
            # Simuler le temps de visionnage
            view_duration = random.uniform(8, 15)
            time.sleep(view_duration)
            return True
        else:
            return False

    except Exception as e:
        return False

def get_problem_accounts():
    """Retourne les comptes problématiques"""
    return problem_accounts

def reset_problem_account(username):
    """Réinitialise un compte problématique"""
    if username in problem_accounts:
        del problem_accounts[username]
        return True
    return False
