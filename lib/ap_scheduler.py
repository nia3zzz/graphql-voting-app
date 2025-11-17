from apscheduler.schedulers.background import BackgroundScheduler
from src.db.database import SessionLocal
from src.models.refresh_token_model import RefreshTokenModel
from datetime import datetime, timedelta


# define the refresh session clean up logic
def clear_refresh_tokens():
    try:
        with SessionLocal.begin() as session:
            # logic to clear old refresh tokens
            expired_sessions = session.query(RefreshTokenModel).filter(
                RefreshTokenModel.last_used_at < datetime.now() - timedelta(days=15)
            )
            expired_sessions.delete()
            print("Task executed!")
    except Exception as e:
        print(f"Error occurred in clear_refresh_tokens: {e}")


scheduler = BackgroundScheduler()

scheduler.add_job(clear_refresh_tokens, "interval", seconds=3600)

# call the function in src/server.py when server starts
background_tasks = scheduler.start
