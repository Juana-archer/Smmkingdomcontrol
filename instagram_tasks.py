# instagram_tasks.py - VERSION AVANCÉE AVEC RÉSOLUTION COMPLÈTE
import requests
import re
import json
import time
import random
from config import COLORS

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

    def validate_cookies(self):
        """Valide que les cookies sont encore actifs"""
        try:
            test_url = "https://www.instagram.com/accounts/edit/"
            response = self.session.get(test_url, timeout=10)
            return 'login' not in response.url
        except:
            return False

    def load_cookies_from_string(self, cookies_str):
        """Charge et valide les cookies"""
        try:
            cookies_dict = json.loads(cookies_str)
            self.session.cookies.update(cookies_dict)
            
            if not self.validate_cookies():
                print(f"{COLORS['R']}[❌] Session expirée - Recréez les cookies{COLORS['S']}")
                return False
                
            print(f"{COLORS['V']}[✅] Session Instagram valide{COLORS['S']}")
            return True
            
        except Exception as e:
            print(f"{COLORS['R']}[❌] Erreur cookies: {e}{COLORS['S']}")
            return False

    def safe_request(self, url, method='GET', data=None, headers=None, retry=True):
        """Requête sécurisée avec gestion d'erreurs avancée"""
        try:
            # Headers par défaut
            default_headers = {
                'X-CSRFToken': self.session.cookies.get('csrftoken', ''),
                'X-Instagram-AJAX': '1',
                'Referer': 'https://www.instagram.com/'
            }
            
            if headers:
                default_headers.update(headers)
                
            # Délai aléatoire
            time.sleep(random.uniform(2, 5))
            
            if method.upper() == 'GET':
                response = self.session.get(url, headers=default_headers, timeout=30)
            else:
                response = self.session.post(url, data=data, headers=default_headers, timeout=30)
            
            # Vérifier les blocages
            if response.status_code == 429:
                print(f"{COLORS['R']}[⏳] Rate limit - Attente 60 secondes{COLORS['S']}")
                time.sleep(60)
                if retry and self.retry_count < self.max_retries:
                    self.retry_count += 1
                    return self.safe_request(url, method, data, headers, False)
                return None
                
            elif response.status_code in [400, 401, 403]:
                print(f"{COLORS['R']}[🔒] Accès refusé - Session probablement bloquée{COLORS['S']}")
                return None
                
            return response
            
        except Exception as e:
            print(f"{COLORS['R']}[🌐] Erreur réseau: {e}{COLORS['S']}")
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

    def like_post_advanced(self, post_url, username):
        """Like avancé avec multiples méthodes"""
        shortcode = self.extract_shortcode(post_url)
        if not shortcode:
            return False

        methods = [
            self._like_graphql,
            self._like_web_api,
            self._like_mobile_api
        ]
        
        for method in methods:
            if method(shortcode, post_url):
                print(f"{COLORS['V']}[❤️] Like réussi ({method.__name__}){COLORS['S']}")
                return True
                
        print(f"{COLORS['R']}[❌] Toutes les méthodes like ont échoué{COLORS['S']}")
        return False

    def _like_graphql(self, shortcode, referer):
        """Like via GraphQL"""
        try:
            url = "https://www.instagram.com/graphql/query/"
            data = {
                'variables': json.dumps({
                    'shortcode': shortcode,
                    'child_comment_count': 0,
                    'fetch_comment_count': 0
                }),
                'doc_id': '2810929249700986'
            }
            
            response = self.safe_request(url, 'POST', data=data)
            return response and response.status_code == 200
        except:
            return False

    def _like_web_api(self, shortcode, referer):
        """Like via API web"""
        try:
            url = f"https://www.instagram.com/web/likes/{shortcode}/like/"
            response = self.safe_request(url, 'POST')
            return response and response.status_code in [200, 201]
        except:
            return False

    def _like_mobile_api(self, shortcode, referer):
        """Like via API mobile"""
        try:
            url = f"https://www.instagram.com/api/v1/web/likes/{shortcode}/like/"
            response = self.safe_request(url, 'POST')
            return response and response.status_code in [200, 201]
        except:
            return False

    def follow_user_advanced(self, profile_url, username):
        """Follow avancé avec multiples méthodes"""
        target_username = self.extract_username(profile_url)
        if not target_username:
            return False

        user_id = self.get_user_id_advanced(target_username)
        if not user_id:
            print(f"{COLORS['R']}[❌] Impossible de trouver {target_username}{COLORS['S']}")
            return False

        methods = [
            self._follow_graphql,
            self._follow_web_api,
            self._follow_mobile_api
        ]
        
        for method in methods:
            if method(user_id, target_username):
                print(f"{COLORS['V']}[➕] Follow réussi ({method.__name__}){COLORS['S']}")
                return True
                
        print(f"{COLORS['R']}[❌] Toutes les méthodes follow ont échoué{COLORS['S']}")
        return False

    def _follow_graphql(self, user_id, username):
        """Follow via GraphQL"""
        try:
            url = "https://www.instagram.com/graphql/query/"
            data = {
                'variables': json.dumps({'user_id': user_id}),
                'doc_id': '3007262092697987'
            }
            
            response = self.safe_request(url, 'POST', data=data)
            return response and response.status_code == 200
        except:
            return False

    def _follow_web_api(self, user_id, username):
        """Follow via API web"""
        try:
            url = f"https://www.instagram.com/web/friendships/{user_id}/follow/"
            response = self.safe_request(url, 'POST')
            return response and response.status_code in [200, 201]
        except:
            return False

    def _follow_mobile_api(self, user_id, username):
        """Follow via API mobile"""
        try:
            url = f"https://www.instagram.com/api/v1/friendships/create/{user_id}/"
            response = self.safe_request(url, 'POST')
            return response and response.status_code in [200, 201]
        except:
            return False

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

    def execute_task(self, task_message, cookies_str, username):
        """Exécution principale avec gestion d'erreurs renforcée"""
        try:
            print(f"{COLORS['C']}[🔧] Exécution tâche pour {username}{COLORS['S']}")
            
            # Charger et valider les cookies
            if not self.load_cookies_from_string(cookies_str):
                return False

            # Délai intelligent
            delay = random.uniform(3, 8)
            print(f"{COLORS['J']}[⏱] Délai de sécurité: {delay:.1f}s{COLORS['S']}")
            time.sleep(delay)

            # Détection d'action
            task_lower = task_message.lower()
            
            if "like" in task_lower:
                post_urls = re.findall(r'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/', task_message)
                for url in post_urls:
                    return self.like_post_advanced(url, username)
                    
            elif "follow" in task_lower or "abonne" in task_lower:
                profile_urls = re.findall(r'https://www\.instagram\.com/[A-Za-z0-9_.]+/', task_message)
                for url in profile_urls:
                    if '/p/' not in url and '/reel/' not in url:
                        return self.follow_user_advanced(url, username)

            print(f"{COLORS['J']}[⚠️] Action non reconnue{COLORS['S']}")
            return False

        except Exception as e:
            print(f"{COLORS['R']}[💥] Erreur critique: {e}{COLORS['S']}")
            return False

def execute_instagram_task(task_message, cookies_str, username):
    """Interface principale"""
    automation = InstagramAutomation()
    return automation.execute_task(task_message, cookies_str, username)
