# app/tasks/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from app.tasks.tasks import daily_summary, cleanup_temp_data
from app.database.session import SessionLocal  # ✅ unified session

# -------------------- Logger Setup --------------------
logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)

# -------------------- Scheduler Instance --------------------
scheduler = BackgroundScheduler()

# -------------------- Scheduler Starter --------------------
def start_scheduler():
    """Start background jobs for daily summary and cleanup tasks."""
    try:
        # Add the daily summary job (runs every 24 hours)
        scheduler.add_job(
            daily_summary,
            trigger=IntervalTrigger(hours=24),
            id="daily_summary_job",
            replace_existing=True
        )

        # Add the cleanup job (runs every 12 hours)
        scheduler.add_job(
            cleanup_temp_data,
            trigger=IntervalTrigger(hours=12),
            id="cleanup_temp_data_job",
            replace_existing=True
        )

        scheduler.start()
        logger.info(f"✅ Scheduler started successfully at {datetime.now()}")

    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")