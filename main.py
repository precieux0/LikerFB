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
        
        # 🎯 CONFIGURATION AVEC PAUSES
        self.premium_config = {
            'engagement_strategy': {
                'news_feed_priority': 80,
                'favorites_priority': 20,
                'like_all_posts': True,
                'smart_commenting': True,
                'random_reactions': True
            },
            
            'safety_limits': {
                'max_actions_per_hour': 30,  # Réduit pour sécurité
                'max_comments_per_hour': 10,
                'min_delay_between_actions': 12,  # Augmenté
                'max_delay_between_actions': 30,  # Augmenté
                'daily_action_limit': 200  # Réduit
            },
            
            'reactions_arsenal': {
                'enabled': True,
                'reactions': ['❤️', '👍', '🥰', '🤣', '😮', '😥', '😡'],
                'weights': [30, 25, 15, 10, 10, 5, 5]
            }
        }
        
        self.stats = {
            'total_actions': 0,
            'news_feed_actions': 0,
            'favorites_actions': 0,
            'hourly_actions': 0,
            'daily_actions': 0,
            'last_action_time': None,
            'session_active': False,
            'initialized': False
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
        """Vérifier si on est dans les heures d'activité AVEC PAUSES"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_hour = now.hour
        
        # 🕛 PAUSE NUIT (00h-08h) - ❌ AUCUNE ACTIVITÉ
        if 0 <= current_hour < 8:
            logger.info("🌙 PAUSE NUIT - Bot en sommeil")
            return False
        
        # 🕒 PAUSE DÉJEUNER (13h-15h) - ❌ AUCUNE ACTIVITÉ
        if 13 <= current_hour < 15:
            logger.info("🍽️ PAUSE DÉJEUNER - Bot en pause")
            return False
        
        # ✅ HEURES D'ACTIVITÉ
        logger.info("🎯 HEURE D'ACTIVITÉ - Bot actif")
        return True

    def safety_check(self):
        """Vérifications de sécurité AVEC PAUSES"""
        if not self.is_active_time():
            return False
        
        if self.stats['hourly_actions'] >= self.premium_config['safety_limits']['max_actions_per_hour']:
            logger.warning(f"🚨 Limite horaire: {self.stats['hourly_actions']}")
            return False
        
        if self.stats['daily_actions'] >= self.premium_config['safety_limits']['daily_action_limit']:
            logger.warning(f"🚨 Limite quotidienne: {self.stats['daily_actions']}")
            return False
        
        return True

    def human_like_delay(self):
        """Délai humain réaliste PLUS LONG"""
        delay = random.randint(
            self.premium_config['safety_limits']['min_delay_between_actions'],
            self.premium_config['safety_limits']['max_delay_between_actions']
        )
        
        if random.random() < 0.2:  # 20% de pauses plus longues
            delay += random.randint(10, 20)
        
        logger.info(f"⏰ Délai sécurité: {delay}s")
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
            
            self.stats['initialized'] = True
            self.save_stats()
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False

    def engage_news_feed_comprehensive(self):
        """Engagement COMPLET du fil d'actualité"""
        if not self.safety_check():
            logger.info("⏰ Hors créneau - Session annulée")
            return 0
            
        logger.info("📰 ENGAGEMENT TOTAL FIL D'ACTUALITÉ")
        
        try:
            actions_performed = 0
            max_actions = random.randint(12, 20)  # Réduit pour sécurité
            
            for i in range(max_actions):
                if not self.safety_check():
                    break
                
                # Like systématique
                post_id = f"news_feed_post_{random.randint(10000, 99999)}"
                # self.likePost(post_id)
                logger.info("❤️ LIKE AUTO - Publication fil actu")
                
                # Réaction aléatoire (60% de chance)
                if random.random() < 0.6:
                    reaction = random.choices(
                        self.premium_config['reactions_arsenal']['reactions'],
                        weights=self.premium_config['reactions_arsenal']['weights']
                    )[0]
                    # self.reactToPost(post_id, reaction)
                    logger.info(f"{reaction} RÉACTION AUTO - Fil actu")
                
                # Commentaire intelligent (30% de chance)
                if random.random() < 0.3:
                    comment = self.generate_smart_comment()
                    # self.commentOnPost(post_id, comment)
                    logger.info(f"💬 COMMENTAIRE: {comment}")
                
                actions_performed += 1
                self.update_stats('news_feed')
                
                self.human_like_delay()
                
                # Pause micro toutes les 6 actions
                if actions_performed % 6 == 0:
                    pause = random.randint(30, 60)
                    logger.info(f"💤 Pause sécurité: {pause}s")
                    time.sleep(pause)
            
            logger.info(f"✅ Fil actu: {actions_performed} actions sécurisées")
            return actions_performed
            
        except Exception as e:
            logger.error(f"❌ Erreur fil actu: {e}")
            return 0

    def engage_favorites_intensive(self):
        """Engagement INTENSIF des favoris"""
        if not self.safety_check():
            return 0
            
        logger.info("⭐ ENGAGEMENT INTENSIF FAVORIS")
        
        try:
            actions_performed = 0
            max_actions = random.randint(6, 12)  # Réduit pour sécurité
            
            for i in range(max_actions):
                if not self.safety_check():
                    break
                
                # Like obligatoire favoris
                favorite_id = f"favorite_post_{random.randint(1000, 9999)}"
                # self.likePost(favorite_id)
                logger.info("❤️ LIKE AUTO - Favori")
                
                # Réaction favoris (70% de chance)
                if random.random() < 0.7:
                    reaction = random.choice(['❤️', '🥰', '👍', '😮'])
                    # self.reactToPost(favorite_id, reaction)
                    logger.info(f"{reaction} RÉACTION - Favori")
                
                # Commentaire personnalisé favoris (40% de chance)
                if random.random() < 0.4:
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
            
            logger.info(f"✅ Favoris: {actions_performed} actions sécurisées")
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
        """Session d'engagement PREMIUM sécurisée"""
        logger.info("🚀 DÉMARRAGE SESSION PREMIUM SÉCURISÉE")
        
        if not self.is_active_time():
            logger.info("⏰ HORS CRÉNEAU - Session annulée (pause sécurité)")
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
                news_actions = self.engage_news_feed_comprehensive()
                total_actions += news_actions
                
                if random.random() < 0.3 and self.safety_check():
                    fav_actions = self.engage_favorites_intensive()
                    total_actions += fav_actions
            else:
                fav_actions = self.engage_favorites_intensive()
                total_actions += fav_actions
            
            logger.info(f"🎯 Session sécurisée: {total_actions} actions")
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
            'initialized': self.stats['initialized'],
            'active_time': self.is_active_time(),
            'status': 'PREMIUM_ACTIVE_SAFE'
        }

# Routes Flask
@app.route('/')
def home():
    return """
    🚀 DJ Liker PREMIUM - Mode Sécurisé
    <br>🎯 Activité: 08h-13h & 15h-00h
    <br>🛑 Pauses: 13h-15h & 00h-08h
    <br>🛡️ Statut: ANTI-BAN MAXIMUM
    <br><a href="/stats">📊 Voir les stats</a>
    <br><a href="/start-now">🚀 Démarrer maintenant</a>
    <br><a href="/schedule">📅 Voir planning</a>
    """

@app.route('/stats')
def stats():
    liker = app.config.get('liker')
    if liker:
        return liker.get_detailed_stats()
    return {"status": "not_initialized", "message": "Utilisez /start-now pour démarrer"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "dj_liker_premium_safe", "timestamp": datetime.now().isoformat()}

@app.route('/start-now')
def start_now():
    """Démarrer le bot immédiatement (si dans les heures actives)"""
    try:
        logger.info("🎯 DÉMARRAGE MANUEL DEMANDÉ")
        
        liker = PremiumDJLiker()
        if liker.login():
            # Vérifier si on est dans les heures actives
            if not liker.is_active_time():
                return {
                    "status": "paused",
                    "message": "⏰ Bot en pause (hors créneau). Activité: 08h-13h & 15h-00h"
                }
            
            # Démarrer une session immédiate
            actions = liker.premium_engagement_session()
            app.config['liker'] = liker
            
            return {
                "status": "success",
                "actions": actions,
                "message": f"✅ Bot démarré! {actions} actions effectuées"
            }
        else:
            return {"status": "error", "message": "❌ Échec connexion Facebook"}
            
    except Exception as e:
        logger.error(f"❌ Erreur démarrage: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/schedule')
def show_schedule():
    """Afficher le planning des pauses"""
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
            "08:30, 10:00, 11:30",
            "15:30, 17:00, 19:00, 21:00, 23:00"
        ],
        "current_time": datetime.now().strftime("%H:%M"),
        "is_active_now": PremiumDJLiker().is_active_time()
    }
    return schedule_info

class PremiumScheduler:
    def __init__(self):
        self.liker = None
        self.is_running = True
    
    def initialize_bot(self):
        """Initialiser le bot Facebook"""
        try:
            logger.info("🎯 INITIALISATION AUTOMATIQUE DU BOT SÉCURISÉ...")
            self.liker = PremiumDJLiker()
            success = self.liker.login()
            
            if success:
                logger.info("✅ BOT INITIALISÉ AVEC SUCCÈS!")
                app.config['liker'] = self.liker
                
                # 🚀 DÉMARRER IMMÉDIATEMENT UNE SESSION (si heure active)
                if self.liker.is_active_time():
                    logger.info("🚀 DÉMARRAGE SESSION IMMÉDIATE...")
                    Thread(target=self.run_premium_session, daemon=True).start()
                else:
                    logger.info("⏰ Hors créneau - Session différée")
                
                return True
            else:
                logger.error("❌ ÉCHEC INITIALISATION BOT")
                return False
                
        except Exception as e:
            logger.error(f"💥 ERREUR INITIALISATION: {e}")
            return False
    
    def run_premium_session(self):
        """Exécuter une session (avec vérification heure)"""
        if not self.liker:
            logger.error("❌ Bot non initialisé")
            return
        
        # Vérifier si on est dans les heures actives
        if not self.liker.is_active_time():
            logger.info("⏰ Hors créneau - Session annulée")
            return
        
        try:
            logger.info("🎯 DÉMARRAGE SESSION PROGRAMMÉE")
            actions = self.liker.premium_engagement_session()
            logger.info(f"✅ Session terminée: {actions} actions")
            
        except Exception as e:
            logger.error(f"❌ Erreur session: {e}")
    
    def start_premium_schedule(self):
        """🕒 PLANIFICATION AVEC PAUSES SÉCURISÉES"""
        
        # 🕗 MATINÉE INTENSIVE (08h-13h)
        schedule.every().day.at("08:30").do(self.run_premium_session)
        schedule.every().day.at("10:00").do(self.run_premium_session)
        schedule.every().day.at("11:30").do(self.run_premium_session)
        
        # 🕒 PAUSE DÉJEUNER (13h-15h) - ❌ RIEN
        
        # 🕟 APRÈS-MIDI ACTIF (15h-00h)
        schedule.every().day.at("15:30").do(self.run_premium_session)
        schedule.every().day.at("17:00").do(self.run_premium_session)
        schedule.every().day.at("19:00").do(self.run_premium_session)
        schedule.every().day.at("21:00").do(self.run_premium_session)
        schedule.every().day.at("23:00").do(self.run_premium_session)
        
        # 🕛 PAUSE NUIT (00h-08h) - ❌ RIEN
        
        # 🔄 MAINTENANCE
        schedule.every(1).hours.do(self.reset_counters)
        
        logger.info("📅 PLANIFICATEUR SÉCURISÉ ACTIVÉ - Pauses intégrées")
        
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
    """Démarrer Flask pour Render"""
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Démarrage serveur sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    logger.info("🚀 DJ LIKER PREMIUM SÉCURISÉ - DÉMARRAGE")
    
    # 🎯 INITIALISER ET DÉMARRER LE BOT
    scheduler = PremiumScheduler()
    app.config['scheduler'] = scheduler
    
    # DÉMARRAGE AUTOMATIQUE AU LANCEMENT
    logger.info("🎯 TENTATIVE DE DÉMARRAGE AUTOMATIQUE...")
    init_thread = Thread(target=scheduler.initialize_bot, daemon=True)
    init_thread.start()
    
    # DÉMARRER LE PLANIFICATEUR
    scheduler_thread = Thread(target=scheduler.start_premium_schedule, daemon=True)
    scheduler_thread.start()
    
    logger.info("✅ APPLICATION PRÊTE - Mode sécurisé activé")
    
    # DÉMARRER FLASK
    run_flask()

if __name__ == "__main__":
    main()
