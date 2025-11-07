# instagram_tasks.py - VERSION COMPLÈTE CORRIGÉE
import time
import random
import re
import os
import json
import tempfile
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, ChallengeRequired

# Gestion des comptes problématiques
problem_accounts = {}

def get_instagram_client(username):
    """
    Récupère un client Instagram COMPATIBLE avec AccountManager
    Utilise les cookies sauvegardés sans reconnexion
    """
    try:
        from account_manager import AccountManager

        account_manager = AccountManager()

        # Vérifier que le compte existe
        if username not in account_manager.accounts:
            print(f"❌ Compte {username} non trouvé dans AccountManager")
            return None

        account_data = account_manager.accounts[username]
        cookies_str = account_data.get('cookies', '')
        password = account_data.get('password')

        if not cookies_str and not password:
            print(f"❌ Aucun cookie ou mot de passe sauvegardé pour {username}")
            return None

        # Vérifier si le compte est marqué problématique
        if is_account_suspended(username):
            print(f"🚫 Compte {username} suspendu - Action bloquée")
            return None

        # Créer le client
        client = Client()
        client.delay_range = [2, 6]  # Délais réalistes

        # NOUVELLE MÉTHODE - CONNEXION DIRECTE AVEC MOT DE PASSE
        if password:
            try:
                print(f"🔄 Connexion directe pour {username}...")
                client.login(username, password)
                
                # Mettre à jour les cookies dans AccountManager
                new_cookies_dict = client.get_cookies()
                new_cookies_str = '; '.join([f"{k}={v}" for k, v in new_cookies_dict.items()])
                account_manager.accounts[username]['cookies'] = new_cookies_str
                account_manager.save_accounts()
                
                print(f"✅ Connexion directe réussie pour {username}")
                
                # Tester la session
                try:
                    print(f"🔍 Test de la session {username}...")
                    client.get_timeline_feed()  # Test simple
                    print(f"✅ Session {username} opérationnelle")
                    return client
                except Exception as test_error:
                    print(f"❌ Session test échoué: {test_error}")
                    mark_account_suspended(username, f"Test session échoué: {test_error}")
                    return None
                    
            except Exception as login_error:
                print(f"❌ Échec connexion directe: {login_error}")
                # Continuer avec la méthode alternative

        # MÉTHODE ALTERNATIVE AVEC COOKIES EXISTANTS
        if cookies_str:
            try:
                print(f"🔄 Tentative avec cookies existants pour {username}...")
                
                # Créer un fichier settings temporaire
                settings = {
                    'cookies': {},
                    'user_agent': 'Instagram 219.0.0.12.117 Android',
                    'uuid': client.state.uuid,
                    'device_id': client.state.device_id,
                    'phone_id': client.state.phone_id,
                    'ad_id': client.state.ad_id,
                }
                
                # Convertir cookies string en format instagrapi
                for cookie in cookies_str.split('; '):
                    if '=' in cookie:
                        key, value = cookie.split('=', 1)
                        settings['cookies'][key.strip()] = value.strip()
                
                # Sauvegarder settings temporairement
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                    json.dump(settings, f)
                    temp_file = f.name
                
                # Charger les settings
                client.load_settings(temp_file)
                os.unlink(temp_file)  # Nettoyer
                
                print(f"✅ Cookies chargés via settings pour {username}")
                
                # Tester la session
                try:
                    print(f"🔍 Test de la session {username}...")
                    client.get_timeline_feed()  # Test simple
                    print(f"✅ Session {username} opérationnelle")
                    return client
                except Exception as test_error:
                    print(f"❌ Session expirée pour {username}: {test_error}")
                    
                    # Tentative de reconnexion si mot de passe disponible
                    if password:
                        try:
                            print(f"🔄 Reconnexion pour {username}...")
                            client.login(username, password)

                            # Mettre à jour les cookies dans AccountManager
                            new_cookies_dict = client.get_cookies()
                            new_cookies_str = '; '.join([f"{k}={v}" for k, v in new_cookies_dict.items()])

                            account_manager.accounts[username]['cookies'] = new_cookies_str
                            account_manager.save_accounts()

                            print(f"✅ Reconnexion réussie pour {username}")
                            return client

                        except Exception as relogin_error:
                            print(f"❌ Échec reconnexion: {relogin_error}")
                            mark_account_suspended(username, f"Échec reconnexion: {relogin_error}")
                            return None
                    else:
                        print(f"❌ Mot de passe non disponible pour {username}")
                        mark_account_suspended(username, "Session expirée - Mot de passe manquant")
                        return None
                        
            except Exception as cookie_error:
                print(f"❌ Erreur gestion cookies: {cookie_error}")
                return None

        print(f"❌ Aucune méthode de connexion disponible pour {username}")
        return None

    except ImportError:
        print("❌ AccountManager non trouvé")
        return None
    except Exception as e:
        print(f"❌ Erreur récupération client: {e}")
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
        # Format attendu: "Comment on post: [texte] https://instagram.com/..."
        comment_patterns = [
            r'comment on post:\s*([^\n]+?)\s*https?://',
            r'comment:\s*([^\n]+?)\s*https?://',
            r'comment\s*"([^"]+)"',
            r'comment\s*\'\'([^\'\']+)\'\'',
        ]

        for pattern in comment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_info['comment_text'] = match.group(1).strip()
                break

        # Si pas trouvé avec les patterns, essayer une méthode simple
        if not task_info['comment_text']:
            # Prendre tout le texte entre "comment" et l'URL
            url_match = re.search(r'https?://[^\s]+', text)
            if url_match:
                url_start = url_match.start()
                comment_part = text[:url_start].lower()
                if 'comment' in comment_part:
                    # Extraire le texte après "comment"
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
    EXÉCUTE DE VRAIES ACTIONS INSTAGRAM de manière SÉCURISÉE
    Version COMPLÈTEMENT COMPATIBLE avec AccountManager
    """
    print(f"\n🎯 Début de tâche pour {username}")
    print(f"📝 Tâche: {task_text[:80]}...")

    # Récupérer le client depuis AccountManager
    client = get_instagram_client(username)
    if not client:
        return False

    # Analyser la tâche
    task_info = analyze_instagram_task(task_text)
    if not task_info:
        print("❌ Impossible d'analyser la tâche")
        return False

    task_type = task_info['type']
    target_url = task_info['link']

    print(f"🔍 Type: {task_type}")
    print(f"🔗 URL: {target_url}")

    try:
        # Exécuter l'action avec gestion d'erreurs
        if 'like' in task_type.lower():
            return like_instagram_post(target_url, client, username)
        elif 'follow' in task_type.lower():
            return follow_instagram_profile(target_url, client, username)
        elif 'comment' in task_type.lower():
            # Passer le texte du commentaire extrait
            comment_text = task_info.get('comment_text', '')
            if not comment_text:
                print("❌ Aucun texte de commentaire trouvé dans la tâche")
                return False
            print(f"💬 Texte du commentaire: \"{comment_text}\"")
            return comment_instagram_post(target_url, client, username, comment_text)
        elif 'story' in task_type.lower():
            return watch_instagram_story(target_url, client, username)
        elif 'video' in task_type.lower():
            return watch_instagram_video(target_url, client, username)
        else:
            print(f"❌ Type de tâche non supporté: {task_type}")
            return False

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def like_instagram_post(post_url, client, username):
    """Like RÉEL d'un post Instagram"""
    try:
        print(f"❤️ Tentative de like...")
        human_delay('like')

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            print("❌ URL invalide")
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            print("❌ Impossible d'extraire l'ID média")
            return False

        # Récupérer l'ID média
        media_id = client.media_id(media_code)
        if not media_id:
            print("❌ Média non trouvé")
            return False

        # Vérifier si déjà liké
        try:
            media_info = client.media_info(media_id)
            if media_info.has_liked:
                print("✅ Déjà liké précédemment")
                return True
        except:
            pass

        # Effectuer le like
        result = client.media_like(media_id)

        if result:
            print(f"✅ Like RÉUSSI sur le post")
            time.sleep(random.uniform(2, 4))
            return True
        else:
            print("❌ Échec du like")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du like: {e}")
        return False

def follow_instagram_profile(profile_url, client, username):
    """Follow RÉEL d'un profil Instagram"""
    try:
        print(f"👤 Tentative de follow...")
        human_delay('follow')

        clean_url = clean_instagram_url(profile_url)
        if not clean_url:
            print("❌ URL invalide")
            return False

        target_username = extract_username_from_url(clean_url)
        if not target_username:
            print("❌ Impossible d'extraire le username")
            return False

        # Récupérer l'ID utilisateur
        user_id = client.user_id_from_username(target_username)
        if not user_id:
            print("❌ Utilisateur non trouvé")
            return False

        # Vérifier si déjà follow
        try:
            user_info = client.user_info(user_id)
            if user_info.following:
                print("✅ Déjà follow précédemment")
                return True
        except:
            pass

        # Effectuer le follow
        result = client.user_follow(user_id)

        if result:
            print(f"✅ Follow RÉUSSI de {target_username}")
            time.sleep(random.uniform(3, 6))
            return True
        else:
            print("❌ Échec du follow")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du follow: {e}")
        return False

def comment_instagram_post(post_url, client, username, comment_text=None):
    """Commentaire RÉEL sur un post Instagram avec texte personnalisé"""
    try:
        print(f"💬 Préparation du commentaire...")
        human_delay('comment')

        clean_url = clean_instagram_url(post_url)
        if not clean_url:
            print("❌ URL invalide")
            return False

        media_code = extract_media_id_from_url(clean_url)
        if not media_code:
            print("❌ Impossible d'extraire l'ID média")
            return False

        media_id = client.media_id(media_code)
        if not media_id:
            print("❌ Média non trouvé")
            return False

        # Vérifier si un texte de commentaire est fourni
        if not comment_text or comment_text.strip() == "":
            print("❌ Aucun texte de commentaire fourni")
            return False

        # Vérifier la longueur du commentaire
        if len(comment_text) > 300:
            comment_text = comment_text[:300] + "..."
            print(f"⚠️ Commentaire tronqué à 300 caractères")

        # Simuler la frappe humaine
        time.sleep(random.uniform(2, 4))

        # Poster le commentaire
        result = client.media_comment(media_id, comment_text)

        if result:
            print(f"✅ Commentaire RÉEL posté avec succès!")
            time.sleep(random.uniform(4, 8))
            return True
        else:
            print("❌ Échec du commentaire")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du commentaire: {e}")
        return False

def watch_instagram_story(story_url, client, username):
    """Visionnage RÉEL d'une story Instagram"""
    try:
        print(f"📖 Tentative de visionnage story...")
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
            print("❌ Aucune story disponible")
            return False

        # Marquer la première story comme vue
        story_id = stories[0].id
        result = client.story_seen([story_id])

        if result:
            print(f"✅ Story RÉELLE marquée comme vue")
            time.sleep(random.uniform(4, 6))
            return True
        else:
            print("❌ Échec du visionnage story")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du visionnage story: {e}")
        return False

def watch_instagram_video(video_url, client, username):
    """Visionnage RÉEL d'une vidéo Instagram"""
    try:
        print(f"🎥 Tentative de visionnage vidéo...")
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
            print(f"✅ Vidéo RÉELLE chargée: {media_info.title or 'Sans titre'}")

            # Simuler le temps de visionnage
            view_duration = random.uniform(8, 15)
            print(f"⏱️ Visionnage simulé: {view_duration:.1f}s")
            time.sleep(view_duration)

            return True
        else:
            print("❌ Vidéo non trouvée")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du visionnage vidéo: {e}")
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

# Test de démonstration
if __name__ == "__main__":
    print("🎯 TEST INSTAGRAM TASKS - VERSION CORRIGÉE")

    # Test avec un compte existant
    test_username = input("Nom d'utilisateur pour test: ").strip()

    if test_username:
        # Test de connexion
        client = get_instagram_client(test_username)
        if client:
            print("✅ Client Instagram opérationnel!")

            # Test d'une tâche commentaire
            test_task = 'Comment on post: "Très beau contenu, continuez comme ça!" https://www.instagram.com/p/Cul9bfhIhCas-9/'
            success = execute_instagram_task(test_task, test_username)
            print(f"Résultat test: {'✅ RÉUSSI' if success else '❌ ÉCHEC'}")
        else:
            print("❌ Impossible de récupérer le client")
    else:
        print("❌ Aucun username fourni")
