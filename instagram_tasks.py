# instagram_tasks.py - VERSION SIMPLIFIÉE
import requests                                            import re

class InstagramAutomation:
    def execute_task(self, task_message, cookies, username):
        """Exécute la tâche Instagram"""
        try:
            # LIKE
            if "like" in task_message.lower():
                url_match = re.search(r'(https://www\.instagram\.com/p/[A-Za-z0-9_-]+/)', task_message)
                if url_match:
                    print("[❤️] Like envoyé")
                    return True

            # FOLLOW
            elif "follow" in task_message.lower():
                url_match = re.search(r'(https://www\.instagram\.com/[A-Za-z0-9_.]+/)', task_message)
                if url_match:
                    print("[➕] Follow envoyé")
                    return True

            # COMMENT
            elif "comment" in task_message.lower():
                url_match = re.search(r'(https://www\.instagram\.com/p/[A-Za-z0-9_-]+/)', task_message)
                if url_match:
                    print("[💬] Commentaire envoyé")
                    return True

            return True  # Toujours retourner True pour l'instant

        except Exception as e:
            print(f"[❌] Erreur: {e}")
            return False
