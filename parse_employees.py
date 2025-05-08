import pandas as pd

# --------------------------
# Shift patterns
# --------------------------
SHIFT_TIMES = {
    "Open": ["10-5"],
    "Close": ["5-11:30"],
}

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def parse_schedule(file_path):
    df = pd.read_excel(file_path)

    employees = []

    for idx, row in df.iterrows():
        name = str(row["Unnamed: 0"]).strip()
        availability = []

        for day in DAYS:
            value = str(row[day]).strip().upper()

            if value == "OFF" or value == "NAN":
                continue

            day_shifts = []

            if value == "ON":
                day_shifts = SHIFT_TIMES["Open"] + SHIFT_TIMES["Close"]

            elif value == "OPEN":
                day_shifts = SHIFT_TIMES["Open"]

            elif value == "CLOSE":
                day_shifts = SHIFT_TIMES["Close"]

            elif "-" in value:
                day_shifts = [value]

            for time in day_shifts:
                # On Saturday, 5-11:30 gets split into A and B
                if time == "5-11:30" and day == "SAT":
                    availability.append(f"{day} 5-11:30 A")
                    availability.append(f"{day} 5-11:30 B")
                else:
                    availability.append(f"{day} {time}")

        ideal_shifts = str(row["Ideal"]).strip()
        ideal_shifts = int(ideal_shifts) if ideal_shifts.isdigit() else 4

        preference = row.get("Preference", 3)
        try:
            preference = int(preference)
        except:
            preference = 3

        employees.append(
            {
                "name": name,
                "availability": availability,
                "ideal_shifts": ideal_shifts,
                "preference": preference,
            }
        )

    return employees


# --------------------------
# Build all unique shifts
# --------------------------
employees = parse_schedule("FOH availability.xlsx")

# REMOVE Geumseong from scheduling
employees = [e for e in employees if e["name"].strip().lower() != "geumseong"]

all_shifts = list({slot for e in employees for slot in e["availability"]})

# --------------------------
# Debugging (optional)
# --------------------------
if __name__ == "__main__":
    for e in employees:
        print(f"\nName: {e['name']}")
        print(f"Available shifts: {e['availability']}")
        print(
            f"Ideal shifts: {e['ideal_shifts']}, Max shifts: {e['max_shifts']}, Preference: {e['preference']}"
        )
