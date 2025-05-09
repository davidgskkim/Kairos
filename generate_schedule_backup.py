from parse_employees import employees, all_shifts

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

# Preferences from spreadsheet
preference = {emp["name"]: emp.get("preference", 3) for emp in employees}
employee_priority = {e["name"]: idx for idx, e in enumerate(employees)}

# -------------------------
# Static preference for working with Geumseong (1 = least prefer, 5 = most prefer)
# -------------------------
preference_with_geumseong = {
    "Sam": 5,
    "Sungwoo": 5,
    "Jonnah": 1,
    "Minal": 4,
    "Minjung": 1,
    "Yujin": 3,
    "Seoyoon": 1,
    "Fionna": 2,
    "Purvesh": 1,
    "Mandy": 5,
}

# -------------------------
# Find Geumseong's shifts
# -------------------------
geumseong_shifts = []
import pandas as pd

df = pd.read_excel("FOH availability.xlsx")
row = df[df["Unnamed: 0"].str.strip().str.lower() == "geumseong"]
if not row.empty:
    for day in DAYS:
        value = str(row.iloc[0][day]).strip().upper()
        if value in ["OPEN", "ON", "CLOSE"]:
            # Same logic as parse_employees
            shifts = []
            if value == "ON":
                shifts = (
                    ["10-5", "5-11:30"]
                    if day != "SAT"
                    else ["10-5", "5-10:30", "5-11:30"]
                )
            elif value == "OPEN":
                shifts = ["10-5"]
            elif value == "CLOSE":
                shifts = ["5-11:30"] if day != "SAT" else ["5-10:30", "5-11:30"]
            for time in shifts:
                if time == "5-11:30" and day == "SAT":
                    geumseong_shifts.append(f"{day} 5-11:30 A")
                    geumseong_shifts.append(f"{day} 5-11:30 B")
                else:
                    geumseong_shifts.append(f"{day} {time}")


# -------------------------
# Helper functions
# -------------------------
def parse_start_end(shift):
    time = shift.split()[1].replace("A", "").replace("B", "").strip()
    start, end = time.split("-")

    def convert(t):
        hr = int(t.split(":")[0]) if ":" in t else int(t)
        minute = int(t.split(":")[1]) if ":" in t else 0
        if hr < 8:
            hr += 12
        return hr + minute / 60

    return convert(start), convert(end)


def shifts_overlap(shift1, shift2):
    day1, time1 = shift1.split()[0], shift1.split()[1]
    day2, time2 = shift2.split()[0], shift2.split()[1]
    if day1 != day2:
        return False
    if ("A" in time1 and "B" in time2) or ("B" in time1 and "A" in time2):
        base1 = time1.replace("A", "").replace("B", "")
        base2 = time2.replace("A", "").replace("B", "")
        if base1 == base2:
            return True
    t1 = time1.replace("A", "").replace("B", "")
    t2 = time2.replace("A", "").replace("B", "")
    if t1 in ["10-5", "12-5"] and t2 in ["10-5", "12-5"]:
        return True
    if t1 in ["5-10:30", "5-11:30"] and t2 in ["5-10:30", "5-11:30"]:
        return True
    s1_start, s1_end = parse_start_end(shift1)
    s2_start, s2_end = parse_start_end(shift2)
    return not (s1_end <= s2_start or s2_end <= s1_start)


# -------------------------
# Preprocess
# -------------------------
remaining_ideal = {e["name"]: e["ideal_shifts"] for e in employees}
assigned_shifts = {e["name"]: [] for e in employees}
availability_clean = {e["name"]: set(e["availability"]) for e in employees}
schedule = {shift: None for shift in all_shifts}

# -------------------------
# Step 1: Rank shifts by flexibility (least flexible first)
# -------------------------
shift_availability = {
    shift: len([e for e in employees if shift in e["availability"]])
    for shift in all_shifts
}

shift_order = sorted(all_shifts, key=lambda s: shift_availability[s])

print("Shift priority order (least to most flexible):")
for s in shift_order:
    print(f"{s}: {shift_availability[s]} available employees")

# -------------------------
# Step 2: Assignment
# -------------------------
for shift in shift_order:
    day = shift.split()[0]
    print(f"\n--- Considering shift {shift} ---")

    possible_emps = []
    for emp in employees:
        name = emp["name"]
        already_working = any(s.startswith(day) for s in assigned_shifts[name])
        overlap = any(shifts_overlap(shift, s) for s in assigned_shifts[name])
        if (
            remaining_ideal[name] > 0
            and shift in emp["availability"]
            and not overlap
            and not already_working
        ):
            possible_emps.append(emp)
        else:
            print(
                f"Skipped {name} for {shift}:",
                {
                    "shift_in_avail": shift in emp["availability"],
                    "remaining_ideal": remaining_ideal[name],
                    "overlap": overlap,
                    "already_working": already_working,
                },
            )

    if possible_emps:

        def sort_key(e):
            # If this shift overlaps Geumseong's shift, sort by 'preference_with_geumseong'
            prefers = preference_with_geumseong.get(e["name"], 3)
            if shift in geumseong_shifts:
                return (
                    employee_priority[e["name"]],
                    5 - prefers,
                )  # Higher prefer = lower sort value
            else:
                return (employee_priority[e["name"]], preference[e["name"]])

        possible_emps.sort(key=sort_key)
        chosen = possible_emps[0]
        name = chosen["name"]
        schedule[shift] = name
        remaining_ideal[name] -= 1
        assigned_shifts[name].append(shift)
        print(f"✅ Assigned {shift} to {name}")
    else:
        print(f"⚠️ No available employee for {shift}")

# -------------------------
# Report
# -------------------------
final_counts = {emp["name"]: 0 for emp in employees}
for assigned_emp in schedule.values():
    if assigned_emp:
        final_counts[assigned_emp] += 1

print("\nFinal assigned shifts per employee (exact quotas target):")
for emp in employees:
    name = emp["name"]
    print(f"{name}: {final_counts[name]} shifts (ideal: {emp['ideal_shifts']})")

print("\nFinal Schedule:")
for day in DAYS:
    day_shifts = sorted(
        [s for s in all_shifts if s.startswith(day)],
        key=lambda x: x.split()[1],
    )
    for shift in day_shifts:
        emp = schedule.get(shift, None)
        if emp:
            print(f"{shift}: {emp}")
        else:
            print(f"{shift}: [Unfilled]")
