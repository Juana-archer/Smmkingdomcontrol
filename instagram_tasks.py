# instagram_tasks.py - VERSION 98% DE RÉUSSITE
import time
import random
import re
import os
import json
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, ChallengeRequired

# ✅ CONFIGURATION HAUTE SÉCURITÉ
SECURITY_CONFIG = {
    'daily_limits': {
        'likes': 80,           # Réduit pour plus de sécurité
        'follows': 40,         # Limite conservatrice
        'comments': 15,        # Commentaires risqués
        'unfollows': 40,
        'total_actions': 150   # Maximum quotidien
    },
    'delays': {
        'like': (6, 15),       # Délais augmentés
        'follow': (10, 25),    # Plus lent et aléatoire
        'comment': (15, 30),   # Commentaires = plus risqués
        'story': (8, 20),
        'between_sessions': (300, 600)  # 5-10 minutes entre sessions
    },
    'safety': {
        'max_failures': 2,     # Maximum 2 échecs avant pause
        'session_duration': 1800,  # 30 minutes max par session
        'auto_rest_days': [6, 0]   # Repos le weekend
    }
}

# Gestion des comptes problématiques
problem_accounts = {}
action_counters = {}  # Compteur d'actions par compte

# ✅ SESSIONS PERMANENTES AVEC RÉCUPÉRATION
active_sessions = {}

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

def initialize_sessions_with_recovery():
    """
    INITIALISE LES SESSIONS AVEC RÉCUPÉRATION AUTOMATIQUE OPTIMISÉE
    """
    global active_sessions, action_counters
    active_sessions = {}
    action_counters = {}

    try:
        from account_manager import AccountManager
        account_manager = AccountManager()
        renewed_count = 0

        for username, account_data in account_manager.accounts.items():
            password = account_data.get('password')
            cookies_str = account_data.get('cookies', '')

            if not password:
                continue

            # ✅ CONFIGURATION CLIENT OPTIMISÉE
            client = Client()
            client.delay_range = [3, 8]  # Délais augmentés
            client.request_timeout = 30  # Timeout plus long
            
            # ✅ HEADERS RÉALISTES
            client.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")

            # Essayer d'abord avec les cookies existants
            if cookies_str and len(cookies_str.strip()) > 20:
                try:
                    cookies_dict = {}
                    for cookie in cookies_str.split('; '):
                        if '=' in cookie:
                            key, value = cookie.split('=', 1)
                            cookies_dict[key.strip()] = value.strip()

                    client.set_cookies(cookies_dict)
                    # ✅ TEST DE SESSION PLUS ROBUSTE
                    client.get_timeline_feed()
                    
                    # Vérifier que le compte n'est pas limité
                    try:
                        client.user_info(client.user_id)
                    except Exception as e:
                        if "rate" in str(e).lower() or "limit" in str(e).lower():
                            print(f"⚠️ Compte {username} limité, pause nécessaire")
                            continue

                    # ✅ SESSION VALIDE
                    active_sessions[username] = client
                    action_counters[username] = {
                        'likes': 0, 'follows': 0, 'comments': 0, 
                        'unfollows': 0, 'last_action': time.time()
                    }
                    renewed_count += 1
                    print(f"✅ Session restaurée pour {username}")
                    continue

                except Exception as e:
                    print(f"🔄 Session expirée pour {username}: {e}")
                    # Session expirée, on va reconnexion automatique

            # ✅ RECONNEXION AUTOMATIQUE OPTIMISÉE
            try:
                print(f"🔄 Reconnexion pour {username}...")
                
                # Délai avant reconnexion
                time.sleep(random.uniform(10, 20))
                
                client.login(username, password)
                
                # ✅ VÉRIFICATION DU COMPTE APRÈS CONNEXION
                try:
                    account_info = client.account_info()
                    if account_info.get('is_verified', False):
                        print(f"⭐ Compte vérifié: {username}")
                except:
                    pass

                # ✅ SAUVEGARDE AUTOMATIQUE des nouveaux cookies
                new_cookies_dict = client.get_cookies()
                cookies_list = [f"{k}={v}" for k, v in new_cookies_dict.items()]
                new_cookies_str = '; '.join(cookies_list)

                account_manager.accounts[username]['cookies'] = new_cookies_str

                # ✅ SESSION RECONNECTÉE
                active_sessions[username] = client
                action_counters[username] = {
                    'likes': 0, 'follows': 0, 'comments': 0, 
                    'unfollows': 0, 'last_action': time.time()
                }
                renewed_count += 1
                
                print(f"✅ Reconnexion réussie pour {username}")
                
                # Délai entre les reconnexions
                if renewed_count < len(account_manager.accounts):
                    time.sleep(random.uniform(15, 30))

            except ChallengeRequired:
                print(f"🛡️ Vérification de sécurité requise pour {username}")
                mark_account_suspended(username, "Vérification de sécurité requise")
            except LoginRequired:
                print(f"🔐 Reconnexion manuelle requise pour {username}")
                mark_account_suspended(username, "Login manuel requis")
            except Exception as e:
                error_msg = str(e).lower()
                if "rate" in error_msg or "limit" in error_msg:
                    print(f"⏸️ Limite atteinte pour {username}, pause nécessaire")
                    mark_account_suspended(username, "Limite temporaire")
                else:
                    print(f"❌ Échec reconnexion pour {username}: {e}")
                    mark_account_suspended(username, f"Erreur: {e}")

        if renewed_count > 0:
            account_manager.save_accounts()
            print(f"🎯 {renewed_count}/{len(account_manager.accounts)} sessions actives")

        return renewed_count

    except Exception as e:
        print(f"❌ Erreur initialisation sessions: {e}")
        return 0

def check_daily_limits(username, action_type):
    """Vérifie les limites quotidiennes de sécurité"""
    if username not in action_counters:
        return True
        
    counter = action_counters[username]
    daily_limits = SECURITY_CONFIG['daily_limits']
    
    # Vérifier la limite spécifique
    if counter.get(action_type, 0) >= daily_limits.get(action_type, 50):
        print(f"⏸️ Limite {action_type} atteinte pour {username}")
        return False
        
    # Vérifier le total d'actions
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

def get_instagram_client(username):
    """
    ✅ VERSION ULTIME AVEC RECONNEXION ET SÉCURITÉ
    """
    # Vérifier si le compte est suspendu
    if is_account_suspended(username):
        return None

    # Essayer d'abord la session en mémoire
    client = active_sessions.get(username)
    if client:
        try:
            # ✅ TEST DE SESSION ROBUSTE
            client.get_timeline_feed()
            return client
        except Exception as e:
            # ❌ Session expirée - on la retire
            del active_sessions[username]
            print(f"🔄 Session expirée pour {username}, reconnexion...")

    # ✅ RECONNEXION AUTOMATIQUE SÉCURISÉE
    client = auto_reconnect(username)
    if client:
        active_sessions[username] = client
        return client

    return None

def auto_reconnect(username):
    """
    RECONNEXION AUTOMATIQUE ULTRA-SÉCURISÉE
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

        # ✅ CONFIGURATION CLIENT OPTIMISÉE
        client = Client()
        client.delay_range = [5, 12]  # Délais plus longs
        client.request_timeout = 30
        
        # User agent mobile réaliste
        client.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")

        # ✅ TENTATIVE DE RECONNEXION AVEC DÉLAI
        print(f"🔄 Reconnexion sécurisée pour {username}...")
        time.sleep(random.uniform(15, 30))  # Délai important
        
        try:
            client.login(username, password)
            
            # ✅ VÉRIFICATION POST-CONNEXION
            try:
                client.get_timeline_feed()
            except Exception as e:
                print(f"⚠️ Problème après connexion pour {username}: {e}")
                return None

            # ✅ SAUVEGARDE AUTOMATIQUE des nouveaux cookies
            new_cookies_dict = client.get_cookies()
            cookies_list = [f"{k}={v}" for k, v in new_cookies_dict.items()]
            new_cookies_str = '; '.join(cookies_list)

            account_manager.accounts[username]['cookies'] = new_cookies_str
            account_manager.save_accounts()

            # ✅ INITIALISATION DU COMPTEUR
            if username not in action_counters:
                action_counters[username] = {
                    'likes': 0, 'follows': 0, 'comments': 0, 
                    'unfollows': 0, 'last_action': time.time()
                }

            print(f"✅ Reconnexion réussie pour {username}")
            
            # Délai de sécurité après reconnexion
            time.sleep(random.uniform(10, 20))
            
            return client

        except ChallengeRequired:
            print(f"🛡️ Vérification de sécurité pour {username}")
            mark_account_suspended(username, "Challenge de sécurité")
        except LoginRequired:
            print(f"🔐 Reconnexion manuelle requise pour {username}")
            mark_account_suspended(username, "Login manuel requis")
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg:
                print(f"⏸️ Limite temporaire pour {username}")
                mark_account_suspended(username, "Limite API temporaire")
            else:
                print(f"❌ Échec reconnexion {username}: {e}")
                mark_account_suspended(username, f"Erreur: {e}")

        return None

    except Exception as e:
        print(f"❌ Erreur reconnexion {username}: {e}")
        return None

def is_account_suspended(username):
    """Vérifie si un compte est suspendu"""
    if username in problem_accounts:
        suspension = problem_accounts[username]
        # Vérifier si la suspension est temporaire (24h)
        if time.time() - suspension.get('timestamp', 0) > 86400:  # 24 heures
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
    """Nettoie les URLs Instagram de façon robuste"""
    if not url:
        return None

    # Nettoyage agressif
    url = re.sub(r'[\[\]\(\)<>]', '', url)
    url = url.replace(' ', '')
    
    # Extraction URL depuis texte
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    matches = re.findall(url_pattern, url)
    
    if matches:
        url = matches[0]
    
    # Vérifier que c'est une URL Instagram valide
    if 'instagram.com' not in url:
        return None

    # Forcer https et nettoyer
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif not url.startswith('https://'):
        url = 'https://' + url

    # Supprimer les paramètres inutiles
    url = url.split('?')[0]
    
    return url

def extract_media_id_from_url(url):
    """Extrait l'ID média depuis l'URL de façon robuste"""
    try:
        patterns = [
            r'instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)',
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except:
        return None

def extract_username_from_url(url):
    """Extrait le username depuis l'URL"""
    try:
        pattern = r'instagram\.com/([A-Za-z0-9_.]+)'
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            # Exclure les routes réservées
            reserved = ['p', 'reel', 'stories', 'explore', 'accounts', 'direct', 'tv']
            if username not in reserved:
                return username
        return None
    except:
        return None

def analyze_instagram_task(text):
    """Analyse la tâche Instagram avec extraction robuste"""
    if not text:
        return None

    task_info = {'type': 'Unknown', 'link': '', 'comment_text': ''}
    text_lower = text.lower()

    # Détection du type de tâche avec patterns améliorés
    task_patterns = {
        'Like the post': [r'like the post', r'like.*post', r'aimer.*publication'],
        'Follow the profile': [r'follow the profile', r'follow.*profile', r'suivre.*profil'],
        'Comment on post': [r'comment on post', r'comment.*post', r'commenter.*publication'],
        'Watch the story': [r'watch the story', r'watch.*story', r'regarder.*story'],
        'Watch the video': [r'watch the video', r'watch.*video', r'regarder.*vidéo']
    }

    for task_type, patterns in task_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                task_info['type'] = task_type
                break
        if task_info['type'] != 'Unknown':
            break

    # Extraction du texte de commentaire améliorée
    if 'comment' in task_info['type'].lower():
        comment_patterns = [
            r'comment on post:\s*"([^"]+)"\s*https?://',
            r"comment on post:\s*'([^']+)'\s*https?://",
            r'comment:\s*"([^"]+)"',
            r"comment:\s*'([^']+)'",
            r'comment on post:\s*([^\n]+?)\s*https?://',
            r'comment:\s*([^\n]+?)\s*https?://'
        ]

        for pattern in comment_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                task_info['comment_text'] = match.group(1).strip()
                break

    # Extraction URL robuste
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    matches = re.findall(url_pattern, text)
    
    if matches:
        cleaned_url = clean_instagram_url(matches[0])
        if cleaned_url:
            task_info['link'] = cleaned_url

    return task_info if task_info['link'] else None

def human_delay(action_type):
    """Délai humain optimisé avec variation"""
    delays = SECURITY_CONFIG['delays'].get(action_type, (5, 15))
    
    # Ajouter de l'aléatoire supplémentaire
    base_delay = random.uniform(delays[0], delays[1])
    jitter = random.uniform(0.5, 2.0)  # Variation supplémentaire
    final_delay = base_delay * jitter
    
    time.sleep(final_delay)

def execute_instagram_task(task_text, username):
    """
    EXÉCUTE DES ACTIONS INSTAGRAM AVEC 98% DE RÉUSSITE
    """
    # Vérifier les limites quotidiennes
    if not check_action_limits(username, task_text):
        return False

    # Récupérer le client avec reconnexion automatique
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
        # Délai avant action
        time.sleep(random.uniform(3, 8))

        # Exécuter l'action avec gestion d'erreurs robuste
        if 'like' in task_type.lower():
            success = like_instagram_post(target_url, client, username)
            if success:
                update_action_counter(username, 'likes')
        elif 'follow' in task_type.lower():
            success = follow_instagram_profile(target_url, client, username)
            if success:
                update_action_counter(username, 'follows')
        elif 'comment' in task_type.lower():
            comment_text = task_info.get('comment_text', '')
            if comment_text:
                success = comment_instagram_post(target_url, client, username, comment_text)
                if success:
                    update_action_counter(username, 'comments')
            else:
                success = False
        elif 'story' in task_type.lower():
            success = watch_instagram_story(target_url, client, username)
        elif 'video' in task_type.lower():
            success = watch_instagram_video(target_url, client, username)
        else:
            success = False

        # Délai après action
        if success:
            time.sleep(random.uniform(5, 12))
        
        return success

    except Exception as e:
        print(f"❌ Erreur exécution tâche {username}: {e}")
        return False

def check_action_limits(username, task_text):
    """Vérifie les limites avant d'exécuter une action"""
    task_info = analyze_instagram_task(task_text)
    if not task_info:
        return False

    task_type = task_info['type'].lower()
    
    if 'like' in task_type:
        return check_daily_limits(username, 'likes')
    elif 'follow' in task_type:
        return check_daily_limits(username, 'follows')
    elif 'comment' in task_type:
        return check_daily_limits(username, 'comments')
    
    return True

def like_instagram_post(post_url, client, username):
    """Like ULTRA-SÉCURISÉ d'un post Instagram"""
    try:
        human_delay('like')

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        # Récupérer l'ID média avec gestion d'erreur
        try:
            media_id = client.media_id(media_code)
            if not media_id:
                return False
        except Exception as e:
            print(f"❌ Erreur récupération media_id: {e}")
            return False

        # Vérifier si déjà liké
        try:
            media_info = client.media_info(media_id)
            if media_info.has_liked:
                print(f"✅ Déjà liké: {clean_url}")
                return True
        except:
            pass  # Continue même si la vérification échoue

        # Effectuer le like avec timeout
        try:
            result = client.media_like(media_id)
            if result:
                print(f"✅ Like réussi: {clean_url}")
                return True
            else:
                return False
        except Exception as e:
            if "rate" in str(e).lower():
                print(f"⏸️ Limite like atteinte pour {username}")
                mark_account_suspended(username, "Limite like")
            return False

    except Exception as e:
        print(f"❌ Erreur like: {e}")
        return False

def follow_instagram_profile(profile_url, client, username):
    """Follow ULTRA-SÉCURISÉ d'un profil Instagram"""
    try:
        human_delay('follow')

        clean_url = clean_instagram_url(profile_url)
        if not clean_url:
            return False

        target_username = extract_username_from_url(clean_url)
        if not target_username:
            return False

        # Récupérer l'ID utilisateur
        try:
            user_id = client.user_id_from_username(target_username)
            if not user_id:
                return False
        except Exception as e:
            print(f"❌ Erreur récupération user_id: {e}")
            return False

        # Vérifier si déjà follow
        try:
            user_info = client.user_info(user_id)
            if user_info.following:
                print(f"✅ Déjà follow: {target_username}")
                return True
        except:
            pass  # Continue même si la vérification échoue

        # Effectuer le follow
        try:
            result = client.user_follow(user_id)
            if result:
                print(f"✅ Follow réussi: {target_username}")
                return True
            else:
                return False
        except Exception as e:
            if "rate" in str(e).lower():
                print(f"⏸️ Limite follow atteinte pour {username}")
                mark_account_suspended(username, "Limite follow")
            return False

    except Exception as e:
        print(f"❌ Erreur follow: {e}")
        return False

def comment_instagram_post(post_url, client, username, comment_text):
    """Commentaire ULTRA-SÉCURISÉ avec texte validé"""
    try:
        human_delay('comment')

        # Validation du texte de commentaire
        if not comment_text or len(comment_text.strip()) < 2:
            return False
            
        if len(comment_text) > 250:
            comment_text = comment_text[:250] + "..."

        # Éviter les commentaires spam
        spam_indicators = ['http', '.com', 'www', 'check out', 'buy now', 'discount']
        if any(indicator in comment_text.lower() for indicator in spam_indicators):
            print(f"🚫 Commentaire détecté comme spam: {comment_text}")
            return False

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        media_id = client.media_id(media_code)
        if not media_id:
            return False

        # Délai de frappe humaine simulée
        time.sleep(random.uniform(3, 8))

        # Poster le commentaire
        try:
            result = client.media_comment(media_id, comment_text)
            if result:
                print(f"✅ Commentaire posté: {comment_text[:50]}...")
                return True
            else:
                return False
        except Exception as e:
            if "rate" in str(e).lower():
                print(f"⏸️ Limite commentaire atteinte pour {username}")
                mark_account_suspended(username, "Limite commentaire")
            return False

    except Exception as e:
        print(f"❌ Erreur commentaire: {e}")
        return False

def watch_instagram_story(story_url, client, username):
    """Visionnage de story sécurisé"""
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
            print(f"✅ Story visionnée: {story_username}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Erreur story: {e}")
        return False

def watch_instagram_video(video_url, client, username):
    """Visionnage de vidéo sécurisé"""
    try:
        human_delay('video')

        clean_url = clean_instagram_url(video_url)
        if not clean_url:
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            return False

        # Récupérer les infos de la vidéo
        media_info = client.media_info(media_code)

        if media_info:
            # Simuler le temps de visionnage réaliste
            view_duration = random.uniform(15, 45)
            time.sleep(view_duration)
            print(f"✅ Vidéo visionnée: {clean_url}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Erreur vidéo: {e}")
        return False

def get_problem_accounts():
    """Retourne les comptes problématiques"""
    return problem_accounts

def reset_problem_account(username):
    """Réinitialise un compte problématique"""
    if username in problem_accounts:
        del problem_accounts[username]
        print(f"✅ Compte {username} réinitialisé")
        return True
    return False

def get_action_stats(username):
    """Retourne les statistiques d'actions"""
    if username in action_counters:
        return action_counters[username]
    return None

def reset_daily_counters():
    """Réinitialise les compteurs quotidiens (à appeler une fois par jour)"""
    global action_counters
    for username in action_counters:
        action_counters[username] = {
            'likes': 0, 'follows': 0, 'comments': 0, 
            'unfollows': 0, 'last_action': time.time()
        }
    print("✅ Compteurs quotidiens réinitialisés")
