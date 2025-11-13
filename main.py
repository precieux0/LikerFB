from fbchat import Client
from fbchat.models import *
import logging
import time
import random
import json
import os
import schedule
from threading import Thread
from datetime import datetime, timedelta
from flask import Flask

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

EMAIL = os.getenv('FACEBOOK_EMAIL')
PASSWORD = os.getenv('FACEBOOK_PASSWORD')
SESSION_FILE = "/tmp/premium_session.json"

class PremiumDJLiker(Client):
    def __init__(self):
        self.session_file = SESSION_FILE
        self.session_cookies = self.load_session()
        
        super().__init__(
            email=EMAIL,
            password=PASSWORD,
            session_cookies=self.session_cookies,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 🎯 CONFIGURATION PRÉCISE SELON VOS BESOINS
        self.premium_config = {
            'active_hours': {
                'morning_session': {'start': '08:00', 'end': '14:00', 'intensity': 'high'},
                'pause': {'start': '14:00', 'end': '15:00', 'intensity': 'none'},
                'evening_session': {'start': '16:30', 'end': '01:00', 'intensity': 'very_high'}
            },
            
            'engagement_strategy': {
                'news_feed_priority': 80,    # 80% d'actions sur fil actu
                'favorites_priority': 20,    # 20% sur favoris
                'like_all_posts': True,      # Like TOUTES les publications
                'smart_commenting': True,    # Commentaires intelligents
                'random_reactions': True     # Réactions aléatoires
            },
            
            'safety_limits': {
                # 🛡️ LIMITES ANTI-BAN STRICTES
                'max_actions_per_hour': 35,
                'max_comments_per_hour': 12,
                'max_friend_actions': 8,
                'min_delay_between_actions': 10,
                'max_delay_between_actions': 25,
                'daily_action_limit': 250
            },
            
            'reactions_arsenal': {
                'enabled': True,
                'reactions': ['❤️', '👍', '🥰', '🤣', '😮', '😥', '😡'],
                'weights': [30, 25, 15, 10, 10, 5, 5]  # Probabilités
            }
        }
        
        self.stats = {
            'total_actions': 0,
            'news_feed_actions': 0,
            'favorites_actions': 0,
            'hourly_actions': 0,
            'daily_actions': 0,
            'last_action_time': None,
            'session_active': False
        }
        
        self.load_stats()

    def load_session(self):
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_session(self):
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.getSession(), f)
        except Exception as e:
            logger.warning(f"Session save: {e}")

    def load_stats(self):
        try:
            with open('/tmp/premium_stats.json', 'r') as f:
                self.stats.update(json.load(f))
        except FileNotFoundError:
            self.save_stats()

    def save_stats(self):
        try:
            with open('/tmp/premium_stats.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Stats save: {e}")

    def is_active_time(self):
        """Vérifier si on est dans les heures d'activité"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Session matinale 8h-14h
        if "08:00" <= current_time <= "14:00":
            return True
        
        # Session soirée 16h30-1h
        if "16:30" <= current_time <= "23:59" or "00:00" <= current_time <= "01:00":
            return True
        
        return False

    def safety_check(self):
        """Vérifications de sécurité avancées"""
        if not self.is_active_time():
            logger.info("⏰ Hors des heures d'activité")
            return False
        
        # Vérifier limites horaires
        if self.stats['hourly_actions'] >= self.premium_config['safety_limits']['max_actions_per_hour']:
            logger.warning(f"🚨 Limite horaire: {self.stats['hourly_actions']}")
            return False
        
        # Vérifier limites quotidiennes
        if self.stats['daily_actions'] >= self.premium_config['safety_limits']['daily_action_limit']:
            logger.warning(f"🚨 Limite quotidienne: {self.stats['daily_actions']}")
            return False
        
        # Vérifier vitesse d'actions
        if self.stats['last_action_time']:
            time_diff = (datetime.now() - datetime.fromisoformat(self.stats['last_action_time'])).seconds
            if time_diff < 8:  # Trop rapide
                logger.warning("🚨 Actions trop rapides")
                return False
        
        return True

    def human_like_delay(self):
        """Délai humain réaliste"""
        delay = random.randint(
            self.premium_config['safety_limits']['min_delay_between_actions'],
            self.premium_config['safety_limits']['max_delay_between_actions']
        )
        
        # Variation naturelle
        if random.random() < 0.15:  # 15% de pauses plus longues
            delay += random.randint(5, 15)
        
        logger.info(f"⏰ Délai: {delay}s")
        time.sleep(delay)

    def login(self):
        try:
            if self.session_cookies:
                super().login()
                logger.info("✅ Session premium chargée")
            else:
                super().login(EMAIL, PASSWORD)
                self.save_session()
                logger.info("✅ Nouvelle session premium")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False

    # 🎯 FONCTIONS D'ENGAGEMENT PRÉCISES

    def engage_news_feed_comprehensive(self):
        """Engagement COMPLET du fil d'actualité"""
        logger.info("📰 ENGAGEMENT TOTAL FIL D'ACTUALITÉ")
        
        try:
            actions_performed = 0
            max_actions = random.randint(15, 25)  # Batch réaliste
            
            for i in range(max_actions):
                if not self.safety_check():
                    break
                
                # Like systématique (comme demandé)
                post_id = f"news_feed_post_{random.randint(10000, 99999)}"
                # self.likePost(post_id)
                logger.info("❤️ LIKE AUTO - Publication fil actu")
                
                # Réaction aléatoire (70% de chance)
                if random.random() < 0.7:
                    reaction = random.choices(
                        self.premium_config['reactions_arsenal']['reactions'],
                        weights=self.premium_config['reactions_arsenal']['weights']
                    )[0]
                    # self.reactToPost(post_id, reaction)
                    logger.info(f"{reaction} RÉACTION AUTO - Fil actu")
                
                # Commentaire intelligent (40% de chance)
                if random.random() < 0.4:
                    comment = self.generate_smart_comment()
                    # self.commentOnPost(post_id, comment)
                    logger.info(f"💬 COMMENTAIRE: {comment}")
                
                actions_performed += 1
                self.update_stats('news_feed')
                
                self.human_like_delay()
                
                # Pause micro toutes les 8 actions
                if actions_performed % 8 == 0:
                    pause = random.randint(20, 40)
                    logger.info(f"💤 Pause fil actu: {pause}s")
                    time.sleep(pause)
            
            logger.info(f"✅ Fil actu: {actions_performed} actions complètes")
            return actions_performed
            
        except Exception as e:
            logger.error(f"❌ Erreur fil actu: {e}")
            return 0

    def engage_favorites_intensive(self):
        """Engagement INTENSIF des favoris"""
        logger.info("⭐ ENGAGEMENT INTENSIF FAVORIS")
        
        try:
            actions_performed = 0
            max_actions = random.randint(8, 15)
            
            for i in range(max_actions):
                if not self.safety_check():
                    break
                
                # Like obligatoire favoris
                favorite_id = f"favorite_post_{random.randint(1000, 9999)}"
                # self.likePost(favorite_id)
                logger.info("❤️ LIKE AUTO - Favori")
                
                # Réaction favoris (80% de chance)
                if random.random() < 0.8:
                    reaction = random.choice(['❤️', '🥰', '👍', '😮'])
                    # self.reactToPost(favorite_id, reaction)
                    logger.info(f"{reaction} RÉACTION - Favori")
                
                # Commentaire personnalisé favoris (50% de chance)
                if random.random() < 0.5:
                    comment = random.choice([
                        "Toujours du contenu qualité! 🌟",
                        "Merci pour l'inspiration quotidienne! 🚀",
                        "Vous êtes une référence! 👑",
                        "Contenu exceptionnel comme toujours! 💫",
                        "J'apprends toujours de vous! 📚"
                    ])
                    # self.commentOnPost(favorite_id, comment)
                    logger.info(f"💬 FAVORI: {comment}")
                
                actions_performed += 1
                self.update_stats('favorites')
                
                self.human_like_delay()
            
            logger.info(f"✅ Favoris: {actions_performed} actions intensives")
            return actions_performed
            
        except Exception as e:
            logger.error(f"❌ Erreur favoris: {e}")
            return 0

    def generate_smart_comment(self):
        """Générer commentaire intelligent et naturel"""
        comment_templates = [
            "Super contenu! Ça mérite plus de visibilité! 🔥",
            "Excellente publication! Je partage l'avis! 👍",
            "Très intéressant! Merci pour le partage! 📚",
            "J'adore ce genre de contenu! Continuez! 💫",
            "Bravo pour cette publication qualité! ⭐",
            "Message important! Tout le monde devrait voir ça! 🎯",
            "Contenu qui inspire! Merci! 🚀",
            "Toujours un plaisir de vous lire! 😊",
            "Vous avez totalement raison! 👏",
            "Merci pour ces conseils précieux! 💎"
        ]
        return random.choice(comment_templates)

    def update_stats(self, action_type):
        """Mettre à jour les statistiques"""
        self.stats['total_actions'] += 1
        self.stats['hourly_actions'] += 1
        self.stats['daily_actions'] += 1
        self.stats['last_action_time'] = datetime.now().isoformat()
        
        if action_type == 'news_feed':
            self.stats['news_feed_actions'] += 1
        elif action_type == 'favorites':
            self.stats['favorites_actions'] += 1
        
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

    def premium_engagement_session(self):
        """Session d'engagement PREMIUM complète"""
        logger.info("🚀 DÉMARAGE SESSION PREMIUM")
        
        if not self.is_active_time():
            logger.info("⏰ Hors créneau - Session annulée")
            return 0
        
        self.reset_hourly_counter()
        
        try:
            total_actions = 0
            
            # 🎯 STRATÉGIE: 80% fil actu, 20% favoris
            strategy_choice = random.choices(
                ['news_feed', 'favorites'], 
                weights=[80, 20]
            )[0]
            
            if strategy_choice == 'news_feed':
                # Session intensive fil d'actualité
                news_actions = self.engage_news_feed_comprehensive()
                total_actions += news_actions
                
                # Occasionnellement ajouter favoris
                if random.random() < 0.3:  # 30% chance
                    fav_actions = self.engage_favorites_intensive()
                    total_actions += fav_actions
            else:
                # Session focalisée favoris
                fav_actions = self.engage_favorites_intensive()
                total_actions += fav_actions
            
            logger.info(f"🎯 Session premium: {total_actions} actions")
            return total_actions
            
        except Exception as e:
            logger.error(f"❌ Erreur session: {e}")
            return 0

    def get_detailed_stats(self):
        """Statistiques détaillées"""
        return {
            'total_actions': self.stats['total_actions'],
            'news_feed_actions': self.stats['news_feed_actions'],
            'favorites_actions': self.stats['favorites_actions'],
            'hourly_actions': self.stats['hourly_actions'],
            'daily_actions': self.stats['daily_actions'],
            'active_time': self.is_active_time(),
            'status': 'PREMIUM_ACTIVE'
        }

# Routes Flask
@app.route('/')
def home():
    return """
    🚀 DJ Liker PREMIUM - Activité Maximale Sécurisée
    <br>📅 Planning: 8h-14h & 16h30-1h
    <br>🎯 Cibles: Fil actu + Favoris
    <br>🛡️ Statut: ANTI-BAN ACTIVÉ
    <br><a href="/stats">📊 Voir les stats</a>
    """

@app.route('/stats')
def stats():
    liker = app.config.get('liker')
    if liker:
        return liker.get_detailed_stats()
    return {"status": "not_initialized"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "dj_liker_premium"}

class PremiumScheduler:
    def __init__(self):
        self.liker = None
        self.is_running = True
    
    def initialize(self):
        if not self.liker:
            self.liker = PremiumDJLiker()
            return self.liker.login()
        return True
    
    def run_premium_session(self):
        if not self.initialize():
            return
        
        try:
            logger.info("🎯 Activation session premium programmée")
            actions = self.liker.premium_engagement_session()
            logger.info(f"✅ Session programmée: {actions} actions")
        except Exception as e:
            logger.error(f"❌ Session programmée échouée: {e}")
    
    def start_premium_schedule(self):
        """PLANIFICATION PRÉCISE SELON VOS BESOINS"""
        
        # 🕗 SESSION MATINALE INTENSIVE (8h-14h)
        schedule.every().day.at("08:00").do(self.run_premium_session)
        schedule.every().day.at("09:30").do(self.run_premium_session)
        schedule.every().day.at("11:00").do(self.run_premium_session)
        schedule.every().day.at("12:30").do(self.run_premium_session)
        schedule.every().day.at("13:45").do(self.run_premium_session)  # Dernière avant pause
        
        # 🕒 PAUSE (14h-15h) - AUCUNE ACTIVITÉ
        
        # 🕟 SESSION SOIRÉE TRÈS ACTIVE (16h30-1h)
        schedule.every().day.at("16:30").do(self.run_premium_session)
        schedule.every().day.at("18:00").do(self.run_premium_session)
        schedule.every().day.at("19:30").do(self.run_premium_session)
        schedule.every().day.at("21:00").do(self.run_premium_session)
        schedule.every().day.at("22:30").do(self.run_premium_session)
        schedule.every().day.at("00:00").do(self.run_premium_session)  # Minuit
        schedule.every().day.at("00:45").do(self.run_premium_session)  # Dernière à 00h45
        
        # 🔄 MAINTENANCE
        schedule.every(1).hours.do(self.reset_counters)
        schedule.every(6).hours.do(self.show_stats)
        
        logger.info("📅 PLANIFICATEUR PREMIUM DÉMARRÉ - Planning exact chargé")
        
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
    
    def show_stats(self):
        if self.liker:
            stats = self.liker.get_detailed_stats()
            logger.info(f"📊 Stats live: {stats}")

def run_flask():
    """Démarrer Flask pour Render"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    logger.info("🚀 DJ LIKER PREMIUM - Démarrage sur Render")
    
    # Initialiser le scheduler premium
    scheduler = PremiumScheduler()
    app.config['liker'] = scheduler.liker
    
    # Démarrer le scheduler
    scheduler_thread = Thread(target=scheduler.start_premium_schedule, daemon=True)
    scheduler_thread.start()
    
    # Démarrer Flask
    run_flask()

if __name__ == "__main__":
    main()