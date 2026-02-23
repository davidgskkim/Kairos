from celery import Celery
import os
import requests 

DEFAULT_UPSTASH = "rediss://default:AcLfAAIncDI4MTQyMjZmNjUxYjI0Zjk5OTY5NGViOTcyNGQzMjA2ZXAyNDk4ODc@working-donkey-49887.upstash.io:6379?ssl_cert_reqs=CERT_NONE"
REDIS_URL = os.getenv("REDIS_URL", DEFAULT_UPSTASH)
celery_app = Celery("kairos_worker", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def run_optimization_task():
    from database import SessionLocal
    from logic import generate_roster
    
    db = SessionLocal()
    try:
        print("🤖 Worker: Starting optimization...")
        
        result = generate_roster(db)
        
        try:
            requests.post("http://127.0.0.1:8000/notify/roster_update")
        except:
            print("⚠️ Could not notify API (is it running?)")

        print("✅ Worker: Optimization complete!")
        return result
    except Exception as e:
        print(f"❌ Worker Error: {e}")
        return ["Error during optimization"]
    finally:
        db.close()