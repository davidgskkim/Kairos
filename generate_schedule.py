import pandas as pd
import os

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


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
        if time1.replace("A", "").replace("B", "") == time2.replace("A", "").replace(
            "B", ""
        ):
            return True
    s1_start, s1_end = parse_start_end(shift1)
    s2_start, s2_end = parse_start_end(shift2)
    return not (s1_end <= s2_start or s2_end <= s1_start)


def get_geumseong_shifts(file_path):
    geumseong_shifts = []
    df = pd.read_excel(file_path)
    row = df[df["Unnamed: 0"].str.strip().str.lower() == "geumseong"]
    if row.empty:
        return []

    for day in DAYS:
        value = str(row.iloc[0][day]).strip().upper()
        if value in ["ON", "OPEN", "CLOSE"]:
            if value == "ON":
                shifts = ["10-5", "5-11:30"]
            elif value == "OPEN":
                shifts = ["10-5"]
            elif value == "CLOSE":
                shifts = ["5-11:30"]
            for time in shifts:
                if time == "5-11:30" and day == "SAT":
                    geumseong_shifts.extend([f"{day} 5-11:30 A", f"{day} 5-11:30 B"])
                else:
                    geumseong_shifts.append(f"{day} {time}")
    return geumseong_shifts


# -------------------------
# Main generation logic
# -------------------------
def generate_schedule(employees, file_path):
    all_shifts = list({slot for e in employees for slot in e["availability"]})

    preference = {emp["name"]: emp.get("preference", 3) for emp in employees}
    employee_priority = {e["name"]: idx for idx, e in enumerate(employees)}
    geumseong_shifts = get_geumseong_shifts(file_path)

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

    remaining_ideal = {e["name"]: e["ideal_shifts"] for e in employees}
    assigned_shifts = {e["name"]: [] for e in employees}
    availability_clean = {e["name"]: set(e["availability"]) for e in employees}
    schedule = {shift: None for shift in all_shifts}

    shift_availability = {
        shift: len([e for e in employees if shift in e["availability"]])
        for shift in all_shifts
    }
    shift_order = sorted(all_shifts, key=lambda s: shift_availability[s])

    for shift in shift_order:
        day = shift.split()[0]
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

        if possible_emps:

            def sort_key(e):
                prefers = preference_with_geumseong.get(e["name"], 3)
                if shift in geumseong_shifts:
                    return (employee_priority[e["name"]], 5 - prefers)
                else:
                    return (employee_priority[e["name"]], preference[e["name"]])

            possible_emps.sort(key=sort_key)
            chosen = possible_emps[0]
            name = chosen["name"]
            schedule[shift] = name
            remaining_ideal[name] -= 1
            assigned_shifts[name].append(shift)

        # Return schedule as a dictionary grouped by day for table display
    structured = {day: [] for day in DAYS}
    for shift, emp in schedule.items():
        day, time = shift.split(maxsplit=1)
        structured[day].append((time, emp if emp else "[Unfilled]"))

    # Sort each day's shifts by start time
    for day in structured:
        structured[day].sort(key=lambda s: parse_start_end(f"{day} {s[0]}")[0])

    # Save to Excel
    output_path = os.path.join("static", "latest_schedule.xlsx")
    save_schedule_excel(structured, output_path)

    return structured


def save_schedule_excel(structured_schedule, output_path):
    rows = []
    for day, shifts in structured_schedule.items():
        for time, emp in shifts:
            rows.append({"Day": day, "Time": time, "Employee": emp})
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
