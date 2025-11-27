from sqlalchemy.orm import Session
from models import Employee, ShiftAssignment, ShiftDefinition
from ortools.sat.python import cp_model
from utils import get_shift_sort_key, parse_time_range
import math

def check_overlap(shift_a, shift_b):
    """Returns True if two shifts on the same day overlap."""
    if shift_a.day != shift_b.day: return False
    
    start_a, end_a = parse_time_range(shift_a.time_slot)
    start_b, end_b = parse_time_range(shift_b.time_slot)
    
    # Overlap logic: (StartA < EndB) and (StartB < EndA)
    return max(start_a, start_b) < min(end_a, end_b)

def is_available(emp_slots, target_day, target_time_str):
    """
    Checks if ANY of the employee's slots on 'target_day' cover the 'target_time_str'.
    """
    target_start, target_end = parse_time_range(target_time_str)
    
    # Filter employee's slots for just this day
    day_slots = [slot.time_slot for slot in emp_slots if slot.day == target_day]
    
    for slot_str in day_slots:
        emp_start, emp_end = parse_time_range(slot_str)
        
        # LOGIC: Does the employee slot COVER the target shift?
        # We allow a tiny bit of "fuzziness" (e.g. 15 mins) if you want, but strict is safer.
        # Strict: Emp_Start <= Target_Start AND Emp_End >= Target_End
        
        # Note: If strings are identical, parse_time_range returns same floats, so this works.
        if emp_start <= target_start and emp_end >= target_end:
            return True
            
    return False

def generate_roster(db: Session):
    employees = db.query(Employee).all()
    
    raw_defs = db.query(ShiftDefinition).all()
    shift_defs = sorted(raw_defs, key=get_shift_sort_key)
    
    if not shift_defs: return ["ERROR: No shift requirements defined."]

    num_shifts = len(shift_defs)
    num_employees = len(employees)
    all_shifts = range(num_shifts)
    all_employees = range(num_employees)

    # Calculate Fairness Cap
    if num_employees > 0:
        fair_cap = math.ceil(num_shifts / num_employees) + 1
    else:
        fair_cap = 99

    print(f"⚖️ Fairness Logic: Capping everyone at {fair_cap} shifts.")

    model = cp_model.CpModel()
    shifts = {}
    for e in all_employees:
        for s in all_shifts:
            shifts[(e, s)] = model.NewBoolVar(f'shift_e{e}_s{s}')

    # Constraint A: Each shift <= 1 person
    for s in all_shifts:
        model.Add(sum(shifts[(e, s)] for e in all_employees) <= 1)

    # --- CONSTRAINT B: AVAILABILITY (UPDATED) ---
    for e in all_employees:
        emp = employees[e]
        
        for s in all_shifts:
            target = shift_defs[s]
            
            # Use our new helper to check time coverage
            if not is_available(emp.availabilities, target.day, target.time_slot):
                 # If not available, force assignment to 0
                 model.Add(shifts[(e, s)] == 0)

    # Constraint C: Fairness Cap
    for e in all_employees:
        model.Add(sum(shifts[(e, s)] for s in all_shifts) <= fair_cap)

    # Constraint D: No Overlapping Shifts
    for e in all_employees:
        for s1 in all_shifts:
            for s2 in all_shifts:
                if s1 >= s2: continue
                if check_overlap(shift_defs[s1], shift_defs[s2]):
                    model.Add(shifts[(e, s1)] + shifts[(e, s2)] <= 1)

    # Objective: Maximize Coverage
    model.Maximize(sum(shifts[(e, s)] for e in all_employees for s in all_shifts))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    new_assignments = []
    db.query(ShiftAssignment).delete()

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for s in all_shifts:
            is_filled = False
            for e in all_employees:
                if solver.Value(shifts[(e, s)]) == 1:
                    worker = employees[e]
                    definition = shift_defs[s]
                    
                    db.add(ShiftAssignment(employee_id=worker.id, day=definition.day, time_slot=definition.time_slot))
                    new_assignments.append(f"{definition.day} {definition.time_slot}: {worker.name}")
                    is_filled = True
                    break
            
            if not is_filled:
                definition = shift_defs[s]
                db.add(ShiftAssignment(employee_id=None, day=definition.day, time_slot=definition.time_slot))
                new_assignments.append(f"{definition.day} {definition.time_slot}: UNFILLED")
    else:
        new_assignments.append("ERROR: Constraints are too tight.")

    db.commit()
    return new_assignments