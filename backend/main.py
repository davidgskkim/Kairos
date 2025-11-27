import os
import shutil
from typing import List

from fastapi import FastAPI, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local Imports
from database import get_db
from models import Employee, ShiftDefinition, ShiftAssignment
from logic import generate_roster
from utils import process_excel_file, get_shift_sort_key
from worker import run_optimization_task

# --- App Configuration ---
app = FastAPI(
    title="Kairos API",
    description="Distributed Scheduling Engine using CP-SAT and Celery.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Manager ---
class ConnectionManager:
    """Manages active WebSocket connections for real-time updates."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# --- Pydantic Schemas ---
class ShiftDefSchema(BaseModel):
    id: int
    day: str
    time_slot: str
    class Config:
        from_attributes = True

class ShiftDefCreate(BaseModel):
    day: str
    time_slot: str

class AvailabilitySchema(BaseModel):
    day: str
    time_slot: str
    class Config:
        from_attributes = True

class EmployeeSchema(BaseModel):
    id: int
    name: str
    ideal_shifts: int
    preference_score: int
    availabilities: List[AvailabilitySchema] = []
    class Config:
        from_attributes = True

# --- Routes: Core ---

@app.get("/")
def read_root():
    return {"system": "Kairos", "status": "operational"}

@app.get("/employees", response_model=List[EmployeeSchema])
def get_employees(db: Session = Depends(get_db)):
    """Fetch all staff members and their availability."""
    return db.query(Employee).all()

@app.get("/schedule")
def get_current_schedule(db: Session = Depends(get_db)):
    """Fetch the currently active roster, sorted chronologically."""
    assignments = db.query(ShiftAssignment).all()
    data = []
    
    for a in assignments:
        emp_name = a.employee.name if a.employee else "UNFILLED"
        data.append({
            "text": f"{a.day} {a.time_slot}: {emp_name}",
            "obj": a
        })
    
    # Sort using utility logic
    data.sort(key=lambda x: get_shift_sort_key(x["obj"]))
    return {"roster": [item["text"] for item in data]}

# --- Routes: Configuration ---

@app.get("/config/shifts", response_model=List[ShiftDefSchema])
def get_shift_definitions(db: Session = Depends(get_db)):
    """Fetch defined shift requirements, sorted."""
    shifts = db.query(ShiftDefinition).all()
    return sorted(shifts, key=get_shift_sort_key)

@app.post("/config/shifts")
async def add_shift_definition(shift: ShiftDefCreate, db: Session = Depends(get_db)):
    """Add a new shift requirement."""
    new_def = ShiftDefinition(day=shift.day, time_slot=shift.time_slot)
    db.add(new_def)
    db.commit()
    await manager.broadcast("settings_update")
    return {"status": "success", "id": new_def.id}

@app.delete("/config/shifts/{shift_id}")
async def delete_shift_definition(shift_id: int, db: Session = Depends(get_db)):
    """Remove a shift requirement."""
    db.query(ShiftDefinition).filter(ShiftDefinition.id == shift_id).delete()
    db.commit()
    await manager.broadcast("settings_update")
    return {"status": "deleted"}

# --- Routes: Actions ---

@app.post("/generate")
async def generate_schedule_endpoint():
    """Triggers the Celery worker to calculate the schedule."""
    task = run_optimization_task.delay()
    return {"status": "queued", "task_id": task.id}

@app.post("/upload/roster")
async def upload_roster(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parses an uploaded Excel file, updates the staff database, 
    and notifies clients to refresh.
    """
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        process_excel_file(temp_filename, db)
        await manager.broadcast("settings_update")
        return {"status": "success", "message": "Database updated"}
    except Exception as e:
        print(f"Error processing file: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# --- Routes: Internal/WebSockets ---

@app.post("/notify/roster_update")
async def notify_roster_update():
    """Internal endpoint called by Celery Worker to trigger WebSocket broadcast."""
    await manager.broadcast("roster_update")
    return {"status": "broadcasted"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)