# app/utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks import daily_summary_task, cleanup_expired_sessions, update_stock_prices

scheduler = BackgroundScheduler()

def start_scheduler():
    """Start the background scheduler with all tasks."""

    # ✅ Daily summary task - every day at 6 PM
    scheduler.add_job(
        daily_summary_task,
        CronTrigger(hour=18, minute=0),
        id="daily_summary",
        replace_existing=True
    )

    # ✅ Cleanup expired sessions - every hour
    scheduler.add_job(
        cleanup_expired_sessions,
        CronTrigger(minute=0),
        id="cleanup_guests",
        replace_existing=True
    )

    # ✅ Stock price updater - every 10 minutes
    scheduler.add_job(
        update_stock_prices,
        CronTrigger(minute="*/10"),
        id="update_stock_prices",
        replace_existing=True
    )

    scheduler.start()
    print("🟢 Scheduler started with real tasks")