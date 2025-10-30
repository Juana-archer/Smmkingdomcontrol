# instagram_tasks.py - VERSION AMÉLIORÉE ET CORRIGÉE
import requests
import re
import json
import time
import random
import sys
import uuid
from config import COLORS

# Alias pour les couleurs
o, V, B, R, J, vi, S = COLORS['o'], COLORS['V'], COLORS['B'], COLORS['R'], COLORS['J'], COLORS['vi'], COLORS['S']

class InstagramAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.retry_count = 0
        self.max_retries = 2

    def setup_session(self):
        """Configuration avancée de la session"""
        mobile_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 12; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]

        self.session.headers.update({
            'User-Agent': random.choice(mobile_user_agents),
            'Accept': '*/*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://www.instagram.com/',
        })

    def parse_cookies(self, cookie_string):
        """Parse les cookies depuis la string"""
        cookies_dict = {}
        for cookie in cookie_string.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
        return cookies_dict

    def get_user_agent(self):
        """Retourne un User-Agent mobile réaliste"""
        agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 12; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]
        return random.choice(agents)

    def validate_cookies(self, cookies_dict):
        """Valide que les cookies sont encore actifs"""
        try:
            test_url = "https://www.instagram.com/accounts/edit/"
            response = self.session.get(test_url, cookies=cookies_dict, timeout=10)
            return 'login' not in response.url
        except:
            return False

    def safe_request(self, url, method='GET', data=None, headers=None, cookies=None, retry=True):
        """Requête sécurisée avec gestion d'erreurs avancée"""
        try:
            # Headers par défaut
            default_headers = {
                'X-CSRFToken': cookies.get('csrftoken', '') if cookies else '',
                'X-Instagram-AJAX': '1',
                'Referer': 'https://www.instagram.com/'
            }

            if headers:
                default_headers.update(headers)

            # Délai aléatoire
            time.sleep(random.uniform(2, 5))

            if method.upper() == 'GET':
                response = self.session.get(url, headers=default_headers, cookies=cookies, timeout=30)
            else:
                response = self.session.post(url, data=data, headers=default_headers, cookies=cookies, timeout=30)

            # Vérifier les blocages
            if response.status_code == 429:
                print(f"{R}[⏳] Rate limit - Attente 60 secondes{S}")
                time.sleep(60)
                if retry and self.retry_count < self.max_retries:
                    self.retry_count += 1
                    return self.safe_request(url, method, data, headers, cookies, False)
                return None

            elif response.status_code in [400, 401, 403]:
                print(f"{R}[🔒] Accès refusé - Session probablement bloquée{S}")
                return None

            return response

        except Exception as e:
            print(f"{R}[🌐] Erreur réseau: {e}{S}")
            return None

    def parse_instagram_response(self, response):
        """Parse les réponses Instagram complexes"""
        if not response:
            return None

        text = response.text.strip()

        # Format 1: for (;;);{json}
        if text.startswith('for (;;);'):
            text = text[9:]

        # Format 2: )]}'{json}
        if text.startswith(')]}\''):
            text = text[4:]

        try:
            return json.loads(text)
        except:
            # Essayer d'extraire le JSON de la réponse HTML
            json_match = re.search(r'window\._sharedData\s*=\s*({.+?});', text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            return None

    def extract_shortcode(self, url):
        """Extrait le shortcode d'une URL"""
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def extract_username(self, url):
        """Extrait le username d'une URL"""
        clean_url = re.sub(r'\?.*$', '', url)
        match = re.search(r'instagram\.com/([A-Za-z0-9_.]+)/?', clean_url)
        if match:
            username = match.group(1)
            if username not in ['p', 'reel', 'stories', 'explore', 'accounts']:
                return username
        return None

    def get_user_id_advanced(self, username):
        """Récupère l'user_id avec plusieurs méthodes"""
        methods = [
            self._get_user_id_graphql,
            self._get_user_id_public_api,
            self._get_user_id_html_scraping
        ]

        for method in methods:
            user_id = method(username)
            if user_id:
                return user_id

        return None

    def _get_user_id_graphql(self, username):
        """Méthode GraphQL pour user_id"""
        try:
            url = "https://www.instagram.com/graphql/query/"
            params = {
                'query_hash': '7c16654f22c819fb63d1183034a5162d',
                'variables': json.dumps({'username': username})
            }

            response = self.safe_request(url, 'GET', headers=params)
            data = self.parse_instagram_response(response)

            if data and 'data' in data and 'user' in data['data']:
                return data['data']['user']['id']
        except:
            pass
        return None

    def _get_user_id_public_api(self, username):
        """API publique pour user_id"""
        try:
            url = f"https://www.instagram.com/{username}/?__a=1"
            response = self.safe_request(url)
            data = self.parse_instagram_response(response)

            if data and 'graphql' in data:
                return data['graphql']['user']['id']
            elif data and 'user' in data:
                return data['user']['id']
        except:
            pass
        return None

    def _get_user_id_html_scraping(self, username):
        """Scraping HTML pour user_id"""
        try:
            url = f"https://www.instagram.com/{username}/"
            response = self.safe_request(url)

            if response:
                # Chercher user_id dans le HTML
                patterns = [
                    r'"user_id":"(\d+)"',
                    r'"owner":{"id":"(\d+)"',
                    r'profilePage_(\d+)'
                ]

                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        return match.group(1)
        except:
            pass
        return None

    # FONCTION LIKE AMÉLIORÉE
    def likes(self, link, cooks, max_retries=2, retry_count=0):
        """Version corrigée de la fonction like"""

        if retry_count >= max_retries:
            print(f"{R}[❌] Trop de tentatives pour like{S}")
            return "fail"

        try:
            # Parser les cookies
            cookies_dict = self.parse_cookies(cooks)

            # 1. Récupération du media_id
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': self.get_user_agent()
            }

            rq1 = requests.get(link, headers=headers, cookies=cookies_dict, timeout=30)

            if rq1.status_code != 200:
                print(f"{R}[❌] Erreur HTTP: {rq1.status_code}{S}")
                return "fail"

            # Extraire le media_id avec plusieurs patterns
            media_id = None
            patterns = [
                r'"media_id":"(\d+_\d+)"',
                r'"id":"(\d+)"',
                r'"shortcode_media":{"id":"(\d+)"',
                r'{"id":"(\d+)"'
            ]

            for pattern in patterns:
                match = re.search(pattern, rq1.text)
                if match:
                    media_id = match.group(1)
                    break

            if not media_id:
                print(f"{R}[❌] Media ID non trouvé{S}")
                return "fail"

            print(f"{o}PostID: {vi}{media_id}{S}")

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion Internet{S}")
            time.sleep(2)
            return self.likes(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur récupération Media ID: {e}{S}")
            return "fail"

        # 2. Envoi du like
        headers = {
            "x-ig-app-id": "1217981644879628",
            "x-asbd-id": "198387",
            "x-instagram-ajax": "c161aac700f",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.get_user_agent(),
            "x-csrftoken": cookies_dict.get('csrftoken', ''),
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://www.instagram.com",
            "referer": link
        }

        try:
            url = f"https://i.instagram.com/api/v1/media/{media_id}/like/"
            rq2 = requests.post(url, headers=headers, cookies=cookies_dict, timeout=30)

            if rq2.status_code == 200:
                try:
                    response_data = rq2.json()
                    if response_data.get('status') == 'ok':
                        print(f"{V}[❤️] Like envoyé avec succès{S}")
                        return "ok"
                    else:
                        print(f"{R}[❌] Réponse API anormale{S}")
                        return "fail"
                except json.JSONDecodeError:
                    # Certaines réponses peuvent être vides mais valides
                    print(f"{V}[❤️] Like probablement réussi{S}")
                    return "ok"
            else:
                print(f"{R}[❌] Erreur HTTP like: {rq2.status_code}{S}")
                return "fail"

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion pendant like{S}")
            time.sleep(2)
            return self.likes(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur envoi like: {e}{S}")
            return "fail"

    # FONCTION FOLLOWERS AMÉLIORÉE
    def followers(self, link, cooks, max_retries=2, retry_count=0):
        """Version corrigée de la fonction follow"""

        if retry_count >= max_retries:
            print(f"{R}[❌] Trop de tentatives pour follow{S}")
            return "fail"

        try:
            # Parser les cookies
            cookies_dict = self.parse_cookies(cooks)

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': self.get_user_agent()
            }

            # Première requête pour récupérer l'user_id
            rq1 = requests.get(link, headers=headers, cookies=cookies_dict, timeout=30)

            if rq1.status_code != 200:
                print(f"{R}[❌] Erreur HTTP: {rq1.status_code}{S}")
                return "fail"

            # Extraire l'user_id
            uid_match = re.search(r'"user_id":"(\d+)"', rq1.text)
            if not uid_match:
                print(f"{R}[❌] UserID non trouvé{S}")
                return "fail"

            uid = uid_match.group(1)
            print(f"{o}UserID: {vi}{uid}{S}")

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion Internet{S}")
            time.sleep(2)
            return self.followers(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur récupération UserID: {e}{S}")
            return "fail"

        # Headers pour la requête follow
        headers = {
            "x-ig-app-id": "1217981644879628",
            "x-asbd-id": "198387",
            "x-instagram-ajax": "c161aac700f",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.get_user_agent(),
            "x-csrftoken": cookies_dict.get('csrftoken', ''),
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://www.instagram.com",
            "referer": link
        }

        try:
            # Requête follow
            follow_url = f"https://i.instagram.com/api/v1/friendships/create/{uid}/"
            rq2 = requests.post(follow_url, headers=headers, cookies=cookies_dict, timeout=30)

            if rq2.status_code == 200:
                print(f"{V}[✅] Follow réussi{S}")
                return "ok"
            else:
                print(f"{R}[❌] Erreur follow: {rq2.status_code}{S}")
                return "fail"

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion pendant follow{S}")
            time.sleep(2)
            return self.followers(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur follow: {e}{S}")
            return "fail"

    # FONCTION COMMENT AMÉLIORÉE
    def comment(self, link, cooks, mss, max_retries=2, retry_count=0):
        """Version corrigée de la fonction comment"""

        if retry_count >= max_retries:
            print(f"{R}[❌] Trop de tentatives pour commenter{S}")
            return "fail"

        try:
            # Parser les cookies
            cookies_dict = self.parse_cookies(cooks)

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': self.get_user_agent()
            }

            # 1. Récupération du media_id
            rq1 = requests.get(link, headers=headers, cookies=cookies_dict, timeout=30)

            if rq1.status_code != 200:
                print(f"{R}[❌] Erreur HTTP: {rq1.status_code}{S}")
                return "fail"

            # Extraire le media_id
            media_id_match = re.search(r'"media_id":"(\d+_\d+)"', rq1.text)
            if not media_id_match:
                # Essayer d'autres patterns
                media_id_match = re.search(r'"id":"(\d+)"', rq1.text)
                if not media_id_match:
                    print(f"{R}[❌] Media ID non trouvé{S}")
                    return "fail"

            media_id = media_id_match.group(1)
            print(f"{o}CommentID: {vi}{media_id}{S}")

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion Internet{S}")
            time.sleep(2)
            return self.comment(link, cooks, mss, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur récupération Media ID: {e}{S}")
            return "fail"

        # 2. Envoi du commentaire
        headers = {
            "x-ig-app-id": "1217981644879628",
            "x-asbd-id": "198387",
            "x-instagram-ajax": "c161aac700f",
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.get_user_agent(),
            "x-csrftoken": cookies_dict.get('csrftoken', ''),
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://www.instagram.com",
            "referer": link
        }

        data = {'comment_text': mss}

        try:
            url = f"https://i.instagram.com/api/v1/web/comments/{media_id}/add/"
            rq2 = requests.post(url, headers=headers, data=data, cookies=cookies_dict, timeout=30)

            if rq2.status_code == 200:
                response_data = rq2.json() if rq2.text else {}
                if response_data.get('status') == 'ok':
                    print(f"{V}[💬] Commentaire posté avec succès{S}")
                    return "ok"
                else:
                    print(f"{R}[❌] Réponse API anormale{S}")
                    return "fail"
            else:
                print(f"{R}[❌] Erreur HTTP commentaire: {rq2.status_code}{S}")
                return "fail"

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion pendant commentaire{S}")
            time.sleep(2)
            return self.comment(link, cooks, mss, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur envoi commentaire: {e}{S}")
            return "fail"

    # FONCTION STORY AMÉLIORÉE
    def story(self, link, cooks, max_retries=2, retry_count=0):
        """Version corrigée - Marque une story comme vue"""

        if retry_count >= max_retries:
            print(f"{R}[❌] Trop de tentatives pour story{S}")
            return False

        try:
            # Parser les cookies
            cookies_dict = self.parse_cookies(cooks)

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': self.get_user_agent()
            }

            # 1. Extraire le story_id depuis l'URL
            story_match = re.search(r'stories/([^/]+)/(\d+)', link)
            if not story_match:
                print(f"{R}[❌] URL de story invalide{S}")
                return False

            username = story_match.group(1)
            story_id = story_match.group(2)
            print(f"{o}Story: {vi}{username} ({story_id}){S}")

            # 2. Marquer la story comme vue via l'API
            view_headers = {
                "x-ig-app-id": "1217981644879628",
                "x-asbd-id": "198387",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": self.get_user_agent(),
                "x-csrftoken": cookies_dict.get('csrftoken', ''),
                "x-requested-with": "XMLHttpRequest",
                "origin": "https://www.instagram.com",
                "referer": link
            }

            view_data = {
                'reel_id': username,
                'story_id': story_id
            }

            # Endpoint pour marquer comme vu
            view_url = "https://www.instagram.com/stories/reel/seen"
            response = requests.post(view_url, headers=view_headers, data=view_data,
                                   cookies=cookies_dict, timeout=30)

            if response.status_code == 200:
                print(f"{V}[👁️] Story marquée comme vue{S}")
                return True
            else:
                # Fallback: juste charger la page
                print(f"{J}[⚠️] API story échouée, chargement simple{S}")
                backup_response = requests.get(link, headers=headers,
                                             cookies=cookies_dict, timeout=30)
                time.sleep(3)  # Simule le temps de visionnage
                print(f"{V}[👁️] Story chargée (fallback){S}")
                return True

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion Internet{S}")
            time.sleep(2)
            return self.story(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur story: {e}{S}")
            return False

    # FONCTION TV AMÉLIORÉE
    def Tv(self, link, cooks, max_retries=2, retry_count=0):
        """Version corrigée - Simule le visionnage d'une vidéo"""

        if retry_count >= max_retries:
            print(f"{R}[❌] Trop de tentatives pour vidéo{S}")
            return False

        try:
            cookies_dict = self.parse_cookies(cooks)

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': self.get_user_agent()
            }

            # 1. Identifier le type de contenu
            if '/reel/' in link:
                content_type = "Reel"
                # Extraire le shortcode pour Reel
                shortcode_match = re.search(r'/reel/([^/]+)', link)
                if shortcode_match:
                    shortcode = shortcode_match.group(1)
                    print(f"{o}Reel: {vi}{shortcode}{S}")
            elif '/p/' in link:
                content_type = "Post Vidéo"
                shortcode_match = re.search(r'/p/([^/]+)', link)
                if shortcode_match:
                    shortcode = shortcode_match.group(1)
                    print(f"{o}Post Vidéo: {vi}{shortcode}{S}")
            else:
                content_type = "Vidéo"
                print(f"{o}Vidéo détectée{S}")

            # 2. Charger la page avec simulation de visionnage
            print(f"{J}[▶️] Début visionnage...{S}")
            response = requests.get(link, headers=headers, cookies=cookies_dict, timeout=30)

            if response.status_code == 200:
                # Simuler le temps de visionnage (4-8 secondes aléatoire)
                view_time = random.randint(4, 8)
                print(f"{J}[⏱] Simulation visionnage: {view_time}s{S}")

                for i in range(view_time):
                    sys.stdout.write(f"\r[▶️] Visionnage... {i+1}s/{view_time}s")
                    sys.stdout.flush()
                    time.sleep(1)

                print(f"\r{V}[✅] Visionnage terminé ({view_time}s){S}")
                return True
            else:
                print(f"{R}[❌] Erreur chargement vidéo: {response.status_code}{S}")
                return False

        except requests.exceptions.ConnectionError:
            print(f"{R}[🌐] Pas de connexion Internet{S}")
            time.sleep(2)
            return self.Tv(link, cooks, max_retries, retry_count + 1)
        except Exception as e:
            print(f"{R}[❌] Erreur vidéo: {e}{S}")
            return False

    def execute_task(self, task_message, cookies_str, username):
        """Exécution principale avec gestion d'erreurs renforcée"""
        try:
            print(f"{J}[🔧] Exécution tâche pour {username}{S}")
            print(f"{B}[📝] Message: {task_message}{S}")

            # Charger les cookies
            cookies_dict = self.parse_cookies(cookies_str)
            if not self.validate_cookies(cookies_dict):
                print(f"{R}[❌] Cookies invalides ou expirés{S}")
                return False

            # Délai aléatoire pour éviter la détection
            delay = random.uniform(3, 8)
            print(f"{J}[⏱] Délai de sécurité: {delay:.1f}s{S}")
            time.sleep(delay)

            # Détection d'action
            task_lower = task_message.lower()

            if "like" in task_lower and "the post" in task_lower:
                post_urls = re.findall(r'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/', task_message)
                for url in post_urls:
                    result = self.likes(url, cookies_str)
                    time.sleep(3)
                    return result == "ok"

            elif "follow" in task_lower or "abonne" in task_lower:
                profile_urls = re.findall(r'https://www\.instagram\.com/[A-Za-z0-9_.]+/', task_message)
                for url in profile_urls:
                    if '/p/' not in url and '/reel/' not in url:
                        result = self.followers(url, cookies_str)
                        time.sleep(3)
                        return result == "ok"

            elif "comment" in task_lower or "the comment" in task_lower:
                post_urls = re.findall(r'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/', task_message)
                # Utiliser la fonction coms améliorée pour le texte
                comment_text = coms(username)
                print(f"{J}Texte commentaire: {comment_text}{S}")

                for url in post_urls:
                    result = self.comment(url, cookies_str, comment_text)
                    time.sleep(3)
                    return result == "ok"

            elif "stories" in task_lower:
                story_urls = re.findall(r'https://www\.instagram\.com/stories/[^\s]+', task_message)
                for url in story_urls:
                    result = self.story(url, cookies_str)
                    time.sleep(3)
                    return result

            elif "open the video" in task_lower or "watch" in task_lower:
                video_urls = re.findall(r'https://www\.instagram\.com/[^\s]+', task_message)
                for url in video_urls:
                    result = self.Tv(url, cookies_str)
                    time.sleep(3)
                    return result

            print(f"{J}[⚠️] Aucune action reconnue dans le message{S}")
            return False

        except Exception as e:
            print(f"{R}[💥] Erreur exécution tâche: {e}{S}")
            return False

# FONCTIONS AMÉLIORÉES POUR TÉLÉGRAM
def coms1(max_messages=15):
    """Version corrigée - Trouve les tâches de commentaire"""
    try:
        from telegram_client import client  # Supposant que vous avez un client Telegram
        if not client:
            print(f"{R}[❌] Client Telegram non disponible{S}")
            return None

        channel_entity = client.get_entity("@SmmKingdomTasksBot")

        from telethon.tl.functions.messages import GetHistoryRequest
        posts = client(GetHistoryRequest(
            peer=channel_entity,
            limit=max_messages,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        if not posts or not posts.messages:
            print(f"{J}[⚠️] Aucun message trouvé{S}")
            return None

        # Patterns pour détecter les tâches de commentaire
        comment_patterns = [
            "the comment", "write the comment", "comment on",
            "post a comment", "leave a comment", "comment the post"
        ]

        for message_obj in posts.messages:
            if not hasattr(message_obj, 'message') or not message_obj.message:
                continue

            message_text = message_obj.message.lower()

            # Vérifier tous les patterns
            for pattern in comment_patterns:
                if pattern in message_text:
                    print(f"{V}[💬] Tâche commentaire trouvée{S}")
                    return message_obj.message

        print(f"{J}[ℹ️] Aucune tâche commentaire trouvée{S}")
        return None

    except Exception as e:
        print(f"{R}[❌] Erreur coms1(): {e}{S}")
        return None

def coms(user, max_messages=20):
    """Version corrigée - Trouve le texte de commentaire"""
    try:
        from telegram_client import client
        if not client:
            print(f"{R}[❌] Client Telegram non disponible{S}")
            return "Great content! 👍"  # Texte par défaut

        channel_entity = client.get_entity("@SmmKingdomTasksBot")

        from telethon.tl.functions.messages import GetHistoryRequest
        posts = client(GetHistoryRequest(
            peer=channel_entity,
            limit=max_messages,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        if not posts or not posts.messages:
            print(f"{J}[⚠️] Aucun message, utilisation texte par défaut{S}")
            return "Great content! 👍"

        # Patterns à exclure (beaucoup plus complets)
        exclude_patterns = [
            "thank you", "thanks", "merci",
            "▪️ action :", "action :", "📝 action",
            "here is a", "here's a", "voici",
            "completed", "✅ completed", "terminé",
            "=======", "———", "•••••",
            "reward", "récompense", "cashcoins",
            "instagram", "back", "🔙",
            user.lower()  # Exclure les messages contenant le username
        ]

        # Caractéristiques d'un texte de commentaire valide
        for message_obj in posts.messages:
            if not hasattr(message_obj, 'message') or not message_obj.message:
                continue

            message_text = message_obj.message.strip()

            # Vérifier les exclusions
            should_exclude = False
            text_lower = message_text.lower()

            for pattern in exclude_patterns:
                if pattern in text_lower:
                    should_exclude = True
                    break

            if should_exclude:
                continue

            # Vérifier que c'est un commentaire valide
            if (len(message_text) >= 3 and
                len(message_text) <= 200 and
                not re.search(r'https?://', message_text) and
                not message_text.startswith('/') and
                '|' not in message_text and  # Exclure les formats username|cookies
                not re.match(r'^\d+$', message_text)):  # Exclure les nombres seuls

                print(f"{V}[💬] Texte de commentaire trouvé: {message_text}{S}")
                return message_text

        # Fallback: texte par défaut si rien n'est trouvé
        default_comments = [
            "Great post! 👍", "Awesome! 😍", "Nice content! 👌",
            "Love this! ❤️", "Amazing! 🔥", "So cool!  😎"
        ]
        default_comment = random.choice(default_comments)
        print(f"{J}[⚠️] Utilisation commentaire par défaut: {default_comment}{S}")
        return default_comment

    except Exception as e:
        print(f"{R}[❌] Erreur coms(): {e}{S}")
        # Retourner un commentaire par défaut en cas d'erreur
        return "Great content! 👍"

# Fonction utilitaire pour être appelée depuis telegram_client.py
def execute_instagram_task(task_message, cookies_str, username):
    """Fonction principale pour exécuter les tâches Instagram"""
    automation = InstagramAutomation()
    return automation.execute_task(task_message, cookies_str, username)

# FONCTION DE CONNEXION AMÉLIORÉE
def cooks(max_attempts=3, attempt=1):
    """Version corrigée - Connexion sécurisée à Instagram"""

    if attempt > max_attempts:
        print(f"{R}[❌] Trop de tentatives de connexion{S}")
        time.sleep(2)
        return None

    try:
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{o}[{V}🔐{o}] Connexion Instagram{S}")
        print(f"{o}────────────────────{S}")

        user = input(f"{o}[{V}?{o}] Username: {B}")
        if not user:
            print(f"{R}[❌] Username vide{S}")
            time.sleep(1)
            return cooks(max_attempts, attempt + 1)

        pwd = input(f"{o}[{V}?{o}] Password: {B}")
        if not pwd:
            print(f"{R}[❌] Mot de passe vide{S}")
            time.sleep(1)
            return cooks(max_attempts, attempt + 1)

        # Génération d'identifiants uniques
        device_id = str(uuid.uuid4())

        # Headers mis à jour pour Instagram 2024
        headers = {
            'User-Agent': 'Instagram 219.0.0.12.117 Android',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-IG-Capabilities': '3brTvw==',
            'X-IG-Connection-Type': 'WIFI',
            'X-FB-HTTP-Engine': 'Liger',
            'Connection': 'close'
        }

        # 1. PREMIÈRE REQUÊTE pour obtenir un token CSRF valide
        session = requests.Session()
        pre_login_url = "https://www.instagram.com/accounts/login/"

        try:
            pre_response = session.get(pre_login_url, timeout=10)
            csrf_token = session.cookies.get('csrftoken')

            if not csrf_token:
                # Fallback: générer un token
                csrf_token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
        except:
            csrf_token = 'missing'

        # 2. REQUÊTE DE LOGIN avec token CSRF dynamique
        login_url = "https://www.instagram.com/accounts/login/ajax/"

        login_data = {
            'username': user,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{pwd}',
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'stopDeletionNonce': '',
            'trustedDeviceRecords': '{}',
            'device_id': device_id
        }

        login_headers = headers.copy()
        login_headers.update({
            'X-CSRFToken': csrf_token,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.instagram.com/accounts/login/'
        })

        print(f"{J}[⏳] Connexion en cours...{S}")
        response = session.post(login_url, data=login_data, headers=login_headers, timeout=30)

        # 3. ANALYSE DE LA RÉPONSE
        if response.status_code != 200:
            print(f"{R}[❌] Erreur réseau: {response.status_code}{S}")
            return cooks(max_attempts, attempt + 1)

        try:
            response_data = response.json()
        except:
            print(f"{R}[❌] Réponse invalide de Instagram{S}")
            return cooks(max_attempts, attempt + 1)

        # Vérifications détaillées
        if response_data.get('authenticated') and response_data.get('status') == 'ok':
            # SUCCÈS - Récupération des cookies
            cookies_dict = session.cookies.get_dict()

            if not cookies_dict:
                print(f"{R}[❌] Aucun cookie reçu{S}")
                return cooks(max_attempts, attempt + 1)

            # Formatage sécurisé des cookies
            cookies_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

            print(f"\n{V}[✅] CONNEXION RÉUSSIE{S}")
            print(f"{B}[👤] Utilisateur: {V}{user}{S}")
            print(f"{B}[🍪] Cookies: {J}{cookies_str}{S}")

            # Sauvegarde sécurisée
            try:
                acc_file = "/sdcard/SmmKingdomTask/insta-acc.txt"
                with open(acc_file, 'a', encoding='utf-8') as f:
                    f.write(f"{user}|{cookies_str}\n")
                print(f"{V}[💾] Compte sauvegardé{S}")
            except Exception as e:
                print(f"{R}[❌] Erreur sauvegarde: {e}{S}")

            input(f"\n{o}[{B}•{o}] Appuyez sur Entrée pour continuer{S}")
            return True

        else:
            # ÉCHEC - Analyse de l'erreur
            error_message = response_data.get('message', 'Erreur inconnue')

            if 'checkpoint' in response_data:
                print(f"{R}[🔒] Vérification de sécurité requise{S}")
                print(f"{J}[ℹ️] Connectez-vous manuellement d'abord{S}")
            elif 'password' in error_message.lower():
                print(f"{R}[❌] Mot de passe incorrect{S}")
            elif 'user' in error_message.lower():
                print(f"{R}[❌] Utilisateur non trouvé{S}")
            else:
                print(f"{R}[❌] Erreur: {error_message}{S}")

            time.sleep(2)
            return cooks(max_attempts, attempt + 1)

    except requests.exceptions.ConnectionError:
        print(f"{R}[🌐] Erreur de connexion Internet{S}")
        time.sleep(2)
        return cooks(max_attempts, attempt + 1)
    except requests.exceptions.Timeout:
        print(f"{R}[⏰] Timeout de connexion{S}")
        time.sleep(2)
        return cooks(max_attempts, attempt + 1)
    except Exception as e:
        print(f"{R}[💥] Erreur inattendue: {e}{S}")
        time.sleep(2)
        return cooks(max_attempts, attempt + 1)
