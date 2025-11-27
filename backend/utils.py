import pandas as pd
from sqlalchemy.orm import Session
from models import Employee, Availability, ShiftAssignment
import re

# ==========================================
# PART 1: Time Parsing Helpers (Centralized)
# ==========================================

DAYS_ORDER = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}

def parse_time_range(time_str):
    """
    Converts '2:30-12:30' into start/end integers (e.g. 14.5, 24.5)
    Handles the 'Crossing Midnight' logic.
    """
    try:
        start_s, end_s = time_str.split('-')
        
        def to_24h(t):
            t = t.strip()
            if ":" in t: 
                parts = t.split(":")
                h = int(parts[0])
                m = int(parts[1])
            else: 
                h = int(t)
                m = 0
            
            # Restaurant Logic:
            # 1..7 -> PM (+12), 8..11 -> AM, 12 -> 12
            if h < 8: h += 12
            return h + (m / 60.0)

        start = to_24h(start_s)
        end = to_24h(end_s)

        # If End < Start (e.g. 12.5 < 14.5), it means next day
        if end <= start:
            end += 12
            
        return start, end
    except:
        return 0, 0

def get_shift_sort_key(shift):
    day_str = shift.day.upper() if hasattr(shift, 'day') else ""
    day_val = DAYS_ORDER.get(day_str, 99)
    try:
        time_slot = shift.time_slot if hasattr(shift, 'time_slot') else ""
        s, _ = parse_time_range(time_slot)
        return (day_val, s)
    except: 
        return (day_val, 99)

# ==========================================
# PART 2: Dynamic Excel Parsing
# ==========================================

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
DEFAULT_SHIFTS = { "OPEN": ["10-5"], "CLOSE": ["5-11:30"] }
IGNORE_NAMES = ["LEGEND", "SHIFT TIMES", "NOTES", "OPEN", "CLOSE", "TOTAL", "NAN"]

def clean_name(name: str) -> str:
    if "=" in name or ":" in name: return "" 
    return re.sub(r"[^a-zA-Z ]", "", name).strip()

def parse_legend_from_df(df, name_col):
    dynamic_shifts = DEFAULT_SHIFTS.copy()
    print("🕵️  Scanning for Legend definitions...")
    
    for idx, row in df.iterrows():
        raw_text = str(row[name_col]).strip()
        if "=" in raw_text:
            parts = raw_text.split("=")
            if len(parts) == 2:
                key = parts[0].strip().upper()
                value = parts[1].strip()
                if any(char.isdigit() for char in value):
                    dynamic_shifts[key] = [value]
                    print(f"   found definition: {key} -> {value}")

    # --- THE FIX: SMART 'ON' GENERATION ---
    if "ON" not in dynamic_shifts:
        open_shifts = dynamic_shifts.get("OPEN", [])
        close_shifts = dynamic_shifts.get("CLOSE", [])
        
        if open_shifts and close_shifts:
            # Construct a FULL RANGE.
            # Take Start of OPEN and End of CLOSE.
            # Open: "2:30-7" -> "2:30"
            # Close: "5-12:30" -> "12:30"
            try:
                s_open = open_shifts[0].split('-')[0].strip()
                s_close = close_shifts[0].split('-')[1].strip()
                
                # Create one giant shift
                full_day = f"{s_open}-{s_close}"
                dynamic_shifts["ON"] = [full_day]
                print(f"   auto-generated: ON -> {dynamic_shifts['ON']} (Merged Range)")
            except:
                # Fallback if format is weird
                dynamic_shifts["ON"] = open_shifts + close_shifts
        else:
            dynamic_shifts["ON"] = open_shifts + close_shifts

    return dynamic_shifts

def process_excel_file(file_path: str, db: Session):
    print(f"📂 Reading file: {file_path}")
    df = pd.read_excel(file_path)
    
    name_col = None
    possible_names = ["Name", "Employee", "Staff", "Unnamed: 0"]
    for col in df.columns:
        if str(col).strip() in possible_names:
            name_col = col
            break
    if not name_col: name_col = df.columns[0]

    shift_map = parse_legend_from_df(df, name_col)

    print("🧹 Clearing old database entries...")
    db.query(ShiftAssignment).delete()
    db.query(Availability).delete()
    db.query(Employee).delete()
    
    count = 0
    for idx, row in df.iterrows():
        raw_name = str(row[name_col]).strip()
        if "=" in raw_name or "LEGEND" in raw_name.upper(): continue
        
        name = clean_name(raw_name)
        if not name or name.lower() == "nan" or "SCHEDULE" in name.upper() or name.upper() in IGNORE_NAMES: continue

        ideal_shifts = 99
        if "Ideal" in df.columns:
            val = str(row.get("Ideal", "")).strip()
            if val.isdigit(): ideal_shifts = int(val)

        db_emp = Employee(name=name, ideal_shifts=ideal_shifts, preference_score=3)
        db.add(db_emp)
        db.flush() 

        for col_name in df.columns:
            if col_name == name_col: continue
            day_str = str(col_name).strip().upper()[:3]
            if day_str in DAYS:
                value = str(row[col_name]).strip().upper()
                if value in ["OFF", "NAN", "nan", "None", "."]: continue
                
                day_shifts = []
                if value in shift_map: day_shifts = shift_map[value]
                elif "-" in value: day_shifts = [value]
                
                for time in day_shifts:
                    db.add(Availability(employee_id=db_emp.id, day=day_str, time_slot=time))
        count += 1

    db.commit()
    print(f"✅ Successfully inserted {count} employees.")
    return True