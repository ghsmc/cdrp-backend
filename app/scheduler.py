"""
Background task scheduler for automatic disaster data imports
"""
import schedule
import time
import threading
import logging
from datetime import datetime, timezone
from app.external_apis import DisasterDataIntegrator

logger = logging.getLogger(__name__)


class DisasterDataScheduler:
    """Scheduler for automatic disaster data imports"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        self.running = True
        
        # Schedule earthquake data import every 30 minutes
        schedule.every(30).minutes.do(self._import_earthquake_data)
        
        # Schedule weather alerts import every 15 minutes
        schedule.every(15).minutes.do(self._import_weather_alerts)
        
        # Schedule comprehensive import every 6 hours
        schedule.every(6).hours.do(self._import_all_data)
        
        # Start the scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Disaster data scheduler started")
        
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        logger.info("Disaster data scheduler stopped")
        
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
                
    def _import_earthquake_data(self):
        """Scheduled task for earthquake data import"""
        try:
            logger.info("Starting scheduled earthquake data import")
            imported_count = DisasterDataIntegrator.import_earthquake_data(min_magnitude=4.0)
            logger.info(f"Scheduled earthquake import completed: {imported_count} alerts imported")
        except Exception as e:
            logger.error(f"Scheduled earthquake import failed: {e}")
            
    def _import_weather_alerts(self):
        """Scheduled task for weather alerts import"""
        try:
            logger.info("Starting scheduled weather alerts import")
            imported_count = DisasterDataIntegrator.import_weather_alerts()
            logger.info(f"Scheduled weather alerts import completed: {imported_count} alerts imported")
        except Exception as e:
            logger.error(f"Scheduled weather alerts import failed: {e}")
            
    def _import_all_data(self):
        """Scheduled task for comprehensive data import"""
        try:
            logger.info("Starting scheduled comprehensive data import")
            
            earthquake_count = DisasterDataIntegrator.import_earthquake_data(min_magnitude=3.5)
            weather_count = DisasterDataIntegrator.import_weather_alerts()
            total_count = earthquake_count + weather_count
            
            logger.info(f"Scheduled comprehensive import completed: {total_count} total alerts imported "
                       f"(earthquakes: {earthquake_count}, weather: {weather_count})")
        except Exception as e:
            logger.error(f"Scheduled comprehensive import failed: {e}")


# Global scheduler instance
disaster_scheduler = DisasterDataScheduler()


def init_scheduler(app):
    """Initialize the disaster data scheduler with Flask app context"""
    with app.app_context():
        try:
            disaster_scheduler.start_scheduler()
            logger.info("Disaster data scheduler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize disaster data scheduler: {e}")


def shutdown_scheduler():
    """Shutdown the disaster data scheduler"""
    try:
        disaster_scheduler.stop_scheduler()
        logger.info("Disaster data scheduler shutdown successfully")
    except Exception as e:
        logger.error(f"Error shutting down disaster data scheduler: {e}")