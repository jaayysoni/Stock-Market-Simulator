# app/utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks import daily_summary_task, cleanup_expired_sessions

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run every day at 6 PM (adjust as needed)
    scheduler.add_job(
        daily_summary_task,
        CronTrigger(hour=18, minute=0),
        id="daily_summary",
        replace_existing=True
    )

    # Run cleanup every hour
    scheduler.add_job(
        cleanup_expired_sessions,
        CronTrigger(minute=0),
        id="cleanup_guests",
        replace_existing=True
    )

    scheduler.start()