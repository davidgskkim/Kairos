from database import SessionLocal
from models import ShiftDefinition

db = SessionLocal()

print("🧹 Clearing old shift requirements...")
db.query(ShiftDefinition).delete()

shifts = []

# ==========================================
# CONFIGURATION: THE "IDEAL" 2:30 PM START
# ==========================================

# --- MON-WED (2 People Total) ---
# ideally 2 people work the whole shift (Open to Close)
for day in ["MON", "TUE", "WED"]:
    shifts.append((day, "2:30-12:30")) # Person A (Whole Day)
    shifts.append((day, "2:30-12:30")) # Person B (Whole Day)

# --- THU-SUN (3 People Total) ---
# You said "3 ppl for closing". 
# Usually this means 2 Openers + 1 Swing/Closer who comes later.
for day in ["THU", "FRI", "SAT", "SUN"]:
    shifts.append((day, "2:30-12:30")) # Person A (Whole Day)
    shifts.append((day, "2:30-12:30")) # Person B (Whole Day)
    shifts.append((day, "5-12:30"))    # Person C (Closer / Swing)

# ==========================================

print(f"🌱 Seeding {len(shifts)} shifts starting at 2:30 PM...")
for day, time in shifts:
    db.add(ShiftDefinition(day=day, time_slot=time))

db.commit()
print("✅ Done! Frontend will now show the correct 2:30 start times.")