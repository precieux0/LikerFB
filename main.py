from flask import Flask
import logging
import time
import random
import json
import os
import schedule
from threading import Thread
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/dj_liker_premium.log')
    ]
)
logger = logging.getLogger(__name__)

class UltimateFacebookBot:
    def __init__(self):
        self.setup_driver()
        self.wait = WebDriverWait(self.driver, 20)
        
        # Compte Facebook
        self.email = os.getenv('FACEBOOK_EMAIL')
        self.password = os.getenv('FACEBOOK_PASSWORD')
        
        # Configuration des réactions
        self.reactions = {
            'like': '❤️',
            'love': '🥰', 
            'care': '😍',
            'haha': '😂',
            'wow': '😮',
            'sad': '😢',
            'angry': '😠'
        }
        
        logger.info("🤖 BOT ULTIME FACEBOOK INITIALISÉ")

    def setup_driver(self):
        """Configuration avancée du navigateur"""
        chrome_options = Options()
        
        # Configuration Render
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Furtivité
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self):
        """Connexion robuste à Facebook"""
        try:
            logger.info("🔐 CONNEXION FACEBOOK EN COURS...")
            
            self.driver.get("https://www.facebook.com")
            time.sleep(4)

            # Gestion cookies
            try:
                cookie_buttons = self.driver.find_elements(By.XPATH, "//button[contains(string(), 'Autoriser')]")
                if cookie_buttons:
                    cookie_buttons[0].click()
                    time.sleep(2)
            except:
                pass

            # Email
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            self.slow_type(email_field, self.email)
            logger.info("📧 Email saisi")

            # Mot de passe
            password_field = self.driver.find_element(By.NAME, "pass")
            password_field.clear()
            self.slow_type(password_field, self.password)
            logger.info("🔑 Mot de passe saisi")

            # Connexion
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            logger.info("🖱️ Clic connexion")

            # Attendre connexion
            time.sleep(6)

            # Vérifier connexion
            if "facebook.com" in self.driver.current_url and "login" not in self.driver.current_url:
                logger.info("✅ CONNECTÉ À FACEBOOK !")
                return True
            else:
                logger.error("❌ Échec connexion")
                return False

        except Exception as e:
            logger.error(f"💥 ERREUR CONNEXION: {e}")
            return False

    def slow_type(self, element, text):
        """Taper comme un humain"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def scroll_and_engage(self, max_actions=20):
        """ENGAGEMENT COMPLET CONSTANT sur le fil"""
        try:
            logger.info(f"📰 ENGAGEMENT CONSTANT POUR {max_actions} ACTIONS...")
            
            self.driver.get("https://www.facebook.com")
            time.sleep(5)
            
            actions_performed = 0
            consecutive_failures = 0
            
            while actions_performed < max_actions and consecutive_failures < 5:
                # Chercher des posts à engager
                posts = self.find_engageable_posts()
                
                if posts:
                    post = random.choice(posts)
                    success = self.engage_post(post)
                    
                    if success:
                        actions_performed += 1
                        consecutive_failures = 0
                        logger.info(f"🎯 ACTION #{actions_performed} RÉUSSIE")
                        
                        # Délai variable entre actions
                        delay = random.randint(12, 25)
                        logger.info(f"⏰ Délai: {delay}s")
                        time.sleep(delay)
                    else:
                        consecutive_failures += 1
                else:
                    consecutive_failures += 1
                    logger.info("🔍 Aucun post trouvé, scrolling...")
                
                # Scroller pour nouveaux posts
                self.smart_scroll()
                
                # Petite pause après scroll
                time.sleep(random.randint(3, 7))

            logger.info(f"✅ ENGAGEMENT TERMINÉ: {actions_performed} actions")
            return actions_performed
            
        except Exception as e:
            logger.error(f"❌ Erreur engagement: {e}")
            return 0

    def find_engageable_posts(self):
        """Trouver les posts engageables"""
        try:
            # Sélecteurs pour les posts
            post_selectors = [
                "//div[@role='article']",
                "//div[contains(@class, 'userContentWrapper')]",
                "//div[@data-ad-preview='message']"
            ]
            
            posts = []
            for selector in post_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    posts.extend(elements)
                except:
                    continue
            
            return posts[:10]  # Limiter à 10 posts
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur recherche posts: {e}")
            return []

    def engage_post(self, post_element):
        """Engager un post spécifique (like, réaction, commentaire)"""
        try:
            # Faire défiler jusqu'au post
            self.driver.execute_script("arguments[0].scrollIntoView();", post_element)
            time.sleep(2)
            
            # Décider de l'action (60% like, 30% réaction, 10% commentaire)
            action_choice = random.random()
            
            if action_choice < 0.6:
                return self.like_post(post_element)
            elif action_choice < 0.9:
                return self.react_to_post(post_element)
            else:
                return self.comment_on_post(post_element)
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur engagement post: {e}")
            return False

    def like_post(self, post_element):
        """Like un post"""
        try:
            like_selectors = [
                ".//div[@aria-label='J'aime']",
                ".//span[text()='J'aime']/..",
                ".//div[contains(@aria-label, 'J'aime')]"
            ]
            
            for selector in like_selectors:
                try:
                    like_buttons = post_element.find_elements(By.XPATH, selector)
                    if like_buttons:
                        button = like_buttons[0]
                        self.driver.execute_script("arguments[0].click();", button)
                        logger.info("❤️ LIKE effectué")
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur like: {e}")
            return False

    def react_to_post(self, post_element):
        """Ajouter une réaction"""
        try:
            # Trouver le bouton Like pour ouvrir les réactions
            like_selectors = [
                ".//div[@aria-label='J'aime']",
                ".//span[text()='J'aime']/.."
            ]
            
            for selector in like_selectors:
                try:
                    like_buttons = post_element.find_elements(By.XPATH, selector)
                    if like_buttons:
                        # Passer la souris pour afficher les réactions
                        button = like_buttons[0]
                        self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", button)
                        time.sleep(1)
                        
                        # Choisir une réaction aléatoire
                        reaction = random.choice(list(self.reactions.values()))
                        logger.info(f"{reaction} TENTATIVE RÉACTION")
                        
                        # Pour l'instant, like simple (les réactions nécessitent plus de complexité)
                        self.driver.execute_script("arguments[0].click();", button)
                        logger.info("❤️ RÉACTION (like) effectuée")
                        return True
                        
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur réaction: {e}")
            return self.like_post(post_element)  # Fallback au like

    def comment_on_post(self, post_element):
        """Commenter un post"""
        try:
            # Trouver le champ commentaire
            comment_selectors = [
                ".//div[contains(@aria-label, 'Écrivez un commentaire')]",
                ".//textarea[contains(@placeholder, 'Écrivez un commentaire')]"
            ]
            
            for selector in comment_selectors:
                try:
                    comment_boxes = post_element.find_elements(By.XPATH, selector)
                    if comment_boxes:
                        comment_box = comment_boxes[0]
                        self.driver.execute_script("arguments[0].click();", comment_box)
                        time.sleep(1)
                        
                        # Générer commentaire intelligent
                        comment = self.generate_comment()
                        
                        # Taper le commentaire
                        comment_box.send_keys(comment)
                        time.sleep(2)
                        
                        # Poster
                        post_buttons = post_element.find_elements(By.XPATH, ".//div[@aria-label='Commenter']")
                        if post_buttons:
                            post_buttons[0].click()
                            logger.info(f"💬 COMMENTAIRE: {comment}")
                            return True
                            
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur commentaire: {e}")
            return False

    def generate_comment(self):
        """Générer commentaire intelligent"""
        comments = [
            "Super contenu! 👏",
            "Très intéressant! 👍", 
            "J'adore! 😍",
            "Excellent! 🚀",
            "Bravo! 👑",
            "Génial! 💫",
            "Top! ⭐",
            "Impressionnant! 🔥",
            "Magnifique! 🌟",
            "Fantastique! 💎",
            "Continue comme ça! 🎯",
            "Tu assures! 💪",
            "Trop bien! 😎",
            "Incroyable! 🤩",
            "Parfait! ✅"
        ]
        return random.choice(comments)

    def smart_scroll(self):
        """Scroller intelligemment"""
        scroll_amount = random.randint(400, 900)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.randint(2, 5))

    def engage_favorites(self, max_actions=8):
        """Engagement intensif des favoris"""
        try:
            logger.info("⭐ ENGAGEMENT INTENSIF FAVORIS...")
            
            # Vos pages/groups favoris (À PERSONNALISER)
            favorites = [
                "https://www.facebook.com/groups/musicproducers",
                "https://www.facebook.com/djmag", 
                "https://www.facebook.com/beatport",
                "https://www.facebook.com/EDM",
                "https://www.facebook.com/DJs"
            ]
            
            actions_performed = 0
            
            for profile_url in random.sample(favorites, min(3, len(favorites))):
                if actions_performed >= max_actions:
                    break
                    
                try:
                    logger.info(f"🎯 Visite de {profile_url}")
                    self.driver.get(profile_url)
                    time.sleep(6)
                    
                    # Engager les posts de la page
                    page_actions = self.engage_page_posts(3)  # Max 3 actions par page
                    actions_performed += page_actions
                    
                    # Délai entre les pages
                    time.sleep(random.randint(15, 30))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erreur page favorite: {e}")
                    continue

            return actions_performed
            
        except Exception as e:
            logger.error(f"❌ Erreur favoris: {e}")
            return 0

    def engage_page_posts(self, max_actions):
        """Engager les posts d'une page spécifique"""
        actions = 0
        try:
            posts = self.find_engageable_posts()
            
            for post in posts[:max_actions]:
                if self.engage_post(post):
                    actions += 1
                    time.sleep(random.randint(8, 15))
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur engagement page: {e}")
            
        return actions

    def close(self):
        """Fermer le navigateur"""
        try:
            self.driver.quit()
            logger.info("🔚 Navigateur fermé")
        except:
            pass

class UltimatePremiumDJLiker:
    def __init__(self):
        self.stats = {
            'total_actions': 0,
            'likes': 0,
            'reactions': 0,
            'comments': 0,
            'favorites_actions': 0,
            'hourly_actions': 0,
            'daily_actions': 0,
            'last_action_time': None,
            'status': 'ULTIMATE_BOT_READY'
        }
        
        self.load_stats()
        
        # Configuration ULTIME
        self.config = {
            'max_actions_per_hour': 30,
            'max_actions_per_session': 25,
            'daily_action_limit': 200,
            'min_delay': 10,
            'max_delay': 25,
            'favorites_ratio': 0.3  # 30% d'actions sur favoris
        }

    def load_stats(self):
        try:
            with open('/tmp/premium_stats.json', 'r') as f:
                loaded_stats = json.load(f)
                self.stats.update(loaded_stats)
        except FileNotFoundError:
            self.save_stats()

    def save_stats(self):
        try:
            with open('/tmp/premium_stats.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Stats save: {e}")

    def is_active_time(self):
        """Heures d'activité avec pauses"""
        now = datetime.now()
        current_hour = now.hour
        
        # 🕛 PAUSE NUIT (00h-08h)
        if 0 <= current_hour < 8:
            return False
        
        # 🕒 PAUSE DÉJEUNER (13h-15h)
        if 13 <= current_hour < 15:
            return False
        
        return True

    def safety_check(self):
        """Vérifications de sécurité"""
        if not self.is_active_time():
            return False
        
        if self.stats['hourly_actions'] >= self.config['max_actions_per_hour']:
            logger.warning(f"🚨 Limite horaire: {self.stats['hourly_actions']}")
            return False
        
        if self.stats['daily_actions'] >= self.config['daily_action_limit']:
            logger.warning(f"🚨 Limite quotidienne: {self.stats['daily_actions']}")
            return False
        
        return True

    def update_stats(self, actions, action_type='general'):
        """Mettre à jour les statistiques"""
        self.stats['total_actions'] += actions
        self.stats['hourly_actions'] += actions
        self.stats['daily_actions'] += actions
        self.stats['last_action_time'] = datetime.now().isoformat()
        
        if action_type == 'favorites':
            self.stats['favorites_actions'] += actions
        
        self.save_stats()

    def reset_hourly_counter(self):
        """Reset compteur horaire"""
        now = datetime.now()
        if 'last_hourly_reset' not in self.stats:
            self.stats['last_hourly_reset'] = now.isoformat()
            self.save_stats()
            return
        
        last_reset = datetime.fromisoformat(self.stats['last_hourly_reset'])
        if (now - last_reset).seconds >= 3600:
            self.stats['hourly_actions'] = 0
            self.stats['last_hourly_reset'] = now.isoformat()
            self.save_stats()
            logger.info("🔄 Compteur horaire reset")

    def ultimate_engagement_session(self):
        """SESSION ULTIME D'ENGAGEMENT CONSTANT"""
        logger.info("🚀 DÉMARRAGE SESSION ULTIME CONSTANTE")
        
        if not self.safety_check():
            logger.info("⏰ Session annulée (pause ou limite)")
            return 0
            
        self.reset_hourly_counter()
        
        bot = UltimateFacebookBot()
        total_actions = 0
        
        try:
            if not bot.login():
                return 0
            
            time.sleep(3)
            
            # Stratégie mixte: Fil d'actualité + Favoris
            news_actions = bot.scroll_and_engage(
                max_actions=random.randint(12, 20)
            )
            total_actions += news_actions
            
            # Engagement favoris (30% du temps)
            if random.random() < self.config['favorites_ratio'] and self.safety_check():
                fav_actions = bot.engage_favorites(
                    max_actions=random.randint(5, 10)
                )
                total_actions += fav_actions
                self.update_stats(fav_actions, 'favorites')
            
            self.update_stats(total_actions)
            logger.info(f"🎯 SESSION ULTIME TERMINÉE: {total_actions} actions")
            return total_actions
            
        except Exception as e:
            logger.error(f"💥 ERREUR SESSION: {e}")
            return 0
        finally:
            bot.close()

    def get_detailed_stats(self):
        """Statistiques détaillées"""
        return {
            'total_actions': self.stats['total_actions'],
            'hourly_actions': self.stats['hourly_actions'],
            'daily_actions': self.stats['daily_actions'],
            'favorites_actions': self.stats['favorites_actions'],
            'last_action': self.stats['last_action_time'],
            'active_time': self.is_active_time(),
            'status': self.stats['status'],
            'mode': 'ULTIMATE_CONSTANT_ENGAGEMENT'
        }

# Routes Flask (similaires mais adaptées)
@app.route('/')
def home():
    return """
    🚀 DJ Liker ULTIME - ENGAGEMENT CONSTANT
    <br>🎯 Activité: 08h-13h & 15h-00h
    <br>🛑 Pauses: 13h-15h & 00h-08h  
    <br>❤️ Likes, Réactions, Commentaires RÉELS
    <br>🔄 Engagement constant et intelligent
    <br><a href="/stats">📊 Voir les stats</a>
    <br><a href="/start-now">🚀 Démarrer maintenant</a>
    <br><a href="/schedule">📅 Voir planning</a>
    """

@app.route('/stats')
def stats():
    liker = app.config.get('liker')
    if liker:
        return liker.get_detailed_stats()
    return {"status": "ready", "message": "Bot ultime prêt - Utilisez /start-now"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "ultimate_facebook_bot", "timestamp": datetime.now().isoformat()}

@app.route('/start-now')
def start_now():
    """Démarrer le bot ultime immédiatement"""
    try:
        logger.info("🎯 DÉMARRAGE MANUEL BOT ULTIME DEMANDÉ")
        
        liker = UltimatePremiumDJLiker()
        
        if not liker.is_active_time():
            return {
                "status": "paused", 
                "message": "⏰ Bot en pause. Activité: 08h-13h & 15h-00h"
            }
        
        actions = liker.ultimate_engagement_session()
        app.config['liker'] = liker
        
        return {
            "status": "success",
            "actions": actions,
            "message": f"✅ Bot ULTIME démarré! {actions} actions d'engagement constant",
            "mode": "ULTIMATE_CONSTANT_ENGAGEMENT"
        }
            
    except Exception as e:
        logger.error(f"❌ Erreur démarrage: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/schedule')
def show_schedule():
    """Afficher le planning"""
    schedule_info = {
        "active_periods": [
            "08:00-13:00 → Matinée intensive",
            "15:00-00:00 → Soirée active" 
        ],
        "pauses": [
            "13:00-15:00 → Pause déjeuner",
            "00:00-08:00 → Pause nuit"
        ],
        "sessions_auto": [
            "08:30, 09:45, 11:00, 12:15",
            "15:30, 17:00, 18:30, 20:00, 21:30, 23:00"
        ],
        "engagement_types": ["Likes", "Réactions", "Commentaires", "Favoris"],
        "current_time": datetime.now().strftime("%H:%M"),
        "is_active_now": UltimatePremiumDJLiker().is_active_time(),
        "mode": "ULTIMATE_CONSTANT_ENGAGEMENT"
    }
    return schedule_info

class UltimateScheduler:
    def __init__(self):
        self.liker = None
        self.is_running = True
    
    def initialize_bot(self):
        """Initialiser le bot ultime"""
        try:
            logger.info("🎯 INITIALISATION BOT ULTIME...")
            self.liker = UltimatePremiumDJLiker()
            
            logger.info("✅ BOT ULTIME INITIALISÉ!")
            app.config['liker'] = self.liker
                
            if self.liker.is_active_time():
                logger.info("🚀 DÉMARRAGE SESSION IMMÉDIATE...")
                Thread(target=self.run_ultimate_session, daemon=True).start()
            else:
                logger.info("⏰ Hors créneau - Session différée")
            
            return True
                
        except Exception as e:
            logger.error(f"💥 ERREUR INITIALISATION: {e}")
            return False
    
    def run_ultimate_session(self):
        """Exécuter une session ultime"""
        if not self.liker:
            return
        
        if not self.liker.is_active_time():
            return
        
        try:
            logger.info("🎯 DÉMARRAGE SESSION ULTIME PROGRAMMÉE")
            actions = self.liker.ultimate_engagement_session()
            logger.info(f"✅ Session ultime: {actions} actions")
            
        except Exception as e:
            logger.error(f"❌ Erreur session: {e}")
    
    def start_ultimate_schedule(self):
        """🕒 PLANIFICATION ULTIME CONSTANTE"""
        
        # 🕗 MATINÉE INTENSIVE (plus de sessions)
        schedule.every().day.at("08:30").do(self.run_ultimate_session)
        schedule.every().day.at("09:45").do(self.run_ultimate_session) 
        schedule.every().day.at("11:00").do(self.run_ultimate_session)
        schedule.every().day.at("12:15").do(self.run_ultimate_session)
        
        # 🕒 PAUSE DÉJEUNER (13h-15h)
        
        # 🕟 APRÈS-MIDI/SOIRÉE ACTIVE (sessions rapprochées)
        schedule.every().day.at("15:30").do(self.run_ultimate_session)
        schedule.every().day.at("17:00").do(self.run_ultimate_session)
        schedule.every().day.at("18:30").do(self.run_ultimate_session)
        schedule.every().day.at("20:00").do(self.run_ultimate_session)
        schedule.every().day.at("21:30").do(self.run_ultimate_session)
        schedule.every().day.at("23:00").do(self.run_ultimate_session)
        
        # 🔄 MAINTENANCE
        schedule.every(1).hours.do(self.reset_counters)
        
        logger.info("📅 PLANIFICATEUR ULTIME ACTIVÉ - Engagement constant")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)
    
    def reset_counters(self):
        if self.liker:
            self.liker.reset_hourly_counter()

def run_flask():
    """Démarrer Flask"""
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Démarrage serveur sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    logger.info("🚀 DJ LIKER ULTIME - ENGAGEMENT CONSTANT DÉMARRAGE")
    
    # 🎯 INITIALISER LE BOT ULTIME
    scheduler = UltimateScheduler()
    app.config['scheduler'] = scheduler
    
    # DÉMARRAGE AUTOMATIQUE
    logger.info("🎯 DÉMARRAGE AUTOMATIQUE BOT ULTIME...")
    init_thread = Thread(target=scheduler.initialize_bot, daemon=True)
    init_thread.start()
    
    # DÉMARRER LE PLANIFICATEUR
    scheduler_thread = Thread(target=scheduler.start_ultimate_schedule, daemon=True)
    scheduler_thread.start()
    
    logger.info("✅ BOT ULTIME PRÊT - Engagement constant activé")
    
    # DÉMARRER FLASK
    run_flask()

if __name__ == "__main__":
    main()
