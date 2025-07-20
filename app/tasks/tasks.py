# Background tasks like sending daily summary or cleanups
# app/tasks.py

def daily_summary_task():
    print("📩 Daily portfolio summary triggered.")
    # Add logic: fetch user portfolios, email reports, etc.
    # You can call generate_pdf_report() or send summary email here.

def cleanup_expired_sessions():
    print("🧹 Cleanup expired guest sessions triggered.")
    # Example logic:
    # - Delete guest users older than 1 day
    # - Remove stale portfolio/watchlist records, etc.