from celery import Celery
import os
import requests 

# 1. PASTE YOUR UPSTASH REDIS URL HERE
# (Keep the quotes! It should look like "rediss://default:pass@endpoint:port")
REDIS_URL = "rediss://default:ARpcAAImcDI5YTM5MzgyNzA0MTU0YjYzYjNmMDliMDk4YjA1NGFjMnAyNjc0OA@desired-gar-6748.upstash.io:6379?ssl_cert_reqs=CERT_NONE"

# 2. Configure Celery
# 'kairos_worker' is the name of the queue
# We use the same URL for both the 'broker' (messaging) and 'backend' (results)
celery_app = Celery("kairos_worker", broker=REDIS_URL, backend=REDIS_URL)

# 3. The Task
@celery_app.task
def run_optimization_task():
    # We import inside the function to avoid circular import issues
    from database import SessionLocal
    from logic import generate_roster
    
    db = SessionLocal()
    try:
        print("🤖 Worker: Starting optimization...")
        
        # Run the heavy math
        result = generate_roster(db)
        
        # 4. The "Callback" Trick
        # When done, tell the API to broadcast the update via WebSocket
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