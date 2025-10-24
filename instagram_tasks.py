# instagram_tasks.py - VERSION COMPLÈTE POUR TÂCHES INSTAGRAM
import requests
import re
import json
import time
from config import COLORS

class InstagramAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()

    def setup_session(self):
        """Configure la session avec les headers Instagram"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'Connection': 'keep-alive'
        })

    def load_cookies_from_string(self, cookies_str):
        """Charge les cookies depuis une string JSON"""
        try:
            cookies_dict = json.loads(cookies_str)
            self.session.cookies.update(cookies_dict)
            return True
        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur chargement cookies: {e}{COLORS['S']}")
            return False

    def get_csrf_token(self):
        """Récupère le token CSRF depuis les cookies"""
        return self.session.cookies.get('csrftoken', '')

    def extract_shortcode(self, url):
        """Extrait le shortcode d'une URL Instagram"""
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/stories/[^/]+/([A-Za-z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def extract_username(self, url):
        """Extrait le username d'une URL Instagram"""
        match = re.search(r'instagram\.com/([A-Za-z0-9_.]+)/?', url)
        return match.group(1) if match else None

    def like_post(self, post_url, username):
        """Like un post Instagram"""
        try:
            shortcode = self.extract_shortcode(post_url)
            if not shortcode:
                print(f"{COLORS['R']}[❌] URL post invalide: {post_url}{COLORS['S']}")
                return False

            # URL de l'API pour like
            like_url = f"https://www.instagram.com/web/likes/{shortcode}/like/"

            headers = {
                'X-CSRFToken': self.get_csrf_token(),
                'Referer': post_url,
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459'
            }

            response = self.session.post(like_url, headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"{COLORS['V']}[❤️] Like envoyé sur le post {shortcode}{COLORS['S']}")
                return True
            else:
                print(f"{COLORS['R']}[❌] Erreur like: {response.status_code}{COLORS['S']}")
                return False

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur like: {e}{COLORS['S']}")
            return False

    def follow_user(self, profile_url, username):
        """Follow un utilisateur Instagram"""
        try:
            target_username = self.extract_username(profile_url)
            if not target_username:
                print(f"{COLORS['R']}[❌] URL profil invalide: {profile_url}{COLORS['S']}")
                return False

            # D'abord, récupérer l'user_id du target
            profile_response = self.session.get(f"https://www.instagram.com/{target_username}/?__a=1", timeout=30)

            if profile_response.status_code != 200:
                print(f"{COLORS['R']}[❌] Profil non trouvé: {target_username}{COLORS['S']}")
                return False

            profile_data = profile_response.json()
            user_id = profile_data['graphql']['user']['id']

            # URL de l'API pour follow
            follow_url = f"https://www.instagram.com/web/friendships/{user_id}/follow/"

            headers = {
                'X-CSRFToken': self.get_csrf_token(),
                'Referer': f"https://www.instagram.com/{target_username}/",
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459'
            }

            response = self.session.post(follow_url, headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"{COLORS['V']}[➕] Abonnement à {target_username} réussi{COLORS['S']}")
                return True
            else:
                print(f"{COLORS['R']}[❌] Erreur follow: {response.status_code}{COLORS['S']}")
                return False

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur follow: {e}{COLORS['S']}")
            return False

    def comment_post(self, post_url, comment_text, username):
        """Commenter un post Instagram"""
        try:
            shortcode = self.extract_shortcode(post_url)
            if not shortcode:
                print(f"{COLORS['R']}[❌] URL post invalide: {post_url}{COLORS['S']}")
                return False

            # URL de l'API pour commenter
            comment_url = f"https://www.instagram.com/web/comments/{shortcode}/add/"

            headers = {
                'X-CSRFToken': self.get_csrf_token(),
                'Referer': post_url,
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'comment_text': comment_text,
                'replied_to_comment_id': ''
            }

            response = self.session.post(comment_url, data=data, headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"{COLORS['V']}[💬] Commentaire envoyé: {comment_text}{COLORS['S']}")
                return True
            else:
                print(f"{COLORS['R']}[❌] Erreur commentaire: {response.status_code}{COLORS['S']}")
                return False

        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur commentaire: {e}{COLORS['S']}")
            return False

    def execute_task(self, task_message, cookies_str, username):
        """Exécute la tâche Instagram basée sur le message"""
        try:
            print(f"{COLORS['C']}[🔧] Exécution tâche pour {username}{COLORS['S']}")
            print(f"{COLORS['B']}[📝] Message: {task_message}{COLORS['S']}")

            # Charger les cookies
            if not self.load_cookies_from_string(cookies_str):
                return False

            # LIKE - Détecter les URLs de posts
            if "like" in task_message.lower():
                post_urls = re.findall(r'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/', task_message)
                for url in post_urls:
                    success = self.like_post(url, username)
                    if success:
                        time.sleep(2)  # Délai entre les actions
                    return success

            # FOLLOW - Détecter les URLs de profils
            elif "follow" in task_message.lower() or "abonne" in task_message.lower():
                profile_urls = re.findall(r'https://www\.instagram\.com/[A-Za-z0-9_.]+/', task_message)
                for url in profile_urls:
                    # Éviter les URLs de posts dans les follow
                    if '/p/' not in url and '/reel/' not in url:
                        success = self.follow_user(url, username)
                        if success:
                            time.sleep(2)
                        return success

            # COMMENT - Détecter URLs de posts + texte de commentaire
            elif "comment" in task_message.lower() or "commentaire" in task_message.lower():
                post_urls = re.findall(r'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/', task_message)
                # Extraire le texte du commentaire (première phrase après "comment")
                comment_match = re.search(r'comment[^:]*:\s*([^\n\.]+)', task_message, re.IGNORECASE)
                comment_text = comment_match.group(1).strip() if comment_match else "Super post! 👍"

                for url in post_urls:
                    success = self.comment_post(url, comment_text, username)
                    if success:
                        time.sleep(2)
                    return success

            # TÂCHE AUTOMATIQUE - Détecter n'importe quelle URL Instagram
            else:
                # Essayer de détecter le type d'URL automatiquement
                instagram_urls = re.findall(r'https://www\.instagram\.com/[^\s]+', task_message)

                for url in instagram_urls:
                    if '/p/' in url or '/reel/' in url:
                        # C'est un post - on like
                        success = self.like_post(url, username)
                        if success:
                            time.sleep(2)
                        return success
                    else:
                        # C'est un profil - on follow
                        success = self.follow_user(url, username)
                        if success:
                            time.sleep(2)
                        return success

            print(f"{COLORS['J']}[⚠️] Aucune URL Instagram détectée dans le message{COLORS['S']}")
            return False

        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur exécution tâche: {e}{COLORS['S']}")
            return False

# Fonction utilitaire pour être appelée depuis telegram_client.py
def execute_instagram_task(task_message, cookies_str, username):
    """Fonction principale pour exécuter les tâches Instagram"""
    automation = InstagramAutomation()
    return automation.execute_task(task_message, cookies_str, username)
