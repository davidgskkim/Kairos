import os
from database import engine, SessionLocal, Base
from models import Employee, Availability
from parse_employees import parse_schedule

def init_db():
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    #Find the Excel file
    excel_file = None
    for file in os.listdir("."):
        if file.endswith(".xlsx"):
            excel_file = file
            break
    
    if not excel_file:
        print("❌ No Excel file found in backend/ folder. Skipping data seeding.")
        return

    print(f"Reading data from {excel_file}...")
    
    # Parse file
    employees_data = parse_schedule(excel_file)
    
    db = SessionLocal()
    
    try:
        db.query(Availability).delete()
        db.query(Employee).delete()
        
        for emp_data in employees_data:
            db_emp = Employee(
                name=emp_data["name"],
                ideal_shifts=emp_data["ideal_shifts"],
                preference_score=emp_data["preference"]
            )
            db.add(db_emp)
            db.commit() 
            db.refresh(db_emp) 
            
            for avail_str in emp_data["availability"]:
                parts = avail_str.split(" ", 1)
                if len(parts) == 2:
                    day, time = parts
                    db_avail = Availability(
                        employee_id=db_emp.id,
                        day=day,
                        time_slot=time
                    )
                    db.add(db_avail)
        
        db.commit()
        print(f"✅ Successfully added {len(employees_data)} employees to the database!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()