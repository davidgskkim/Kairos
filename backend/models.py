from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ideal_shifts = Column(Integer, default=4)
    preference_score = Column(Integer, default=3)
    availabilities = relationship("Availability", back_populates="employee")
    assignments = relationship("ShiftAssignment", back_populates="employee")

class Availability(Base):
    __tablename__ = "availabilities"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    day = Column(String)
    time_slot = Column(String)
    employee = relationship("Employee", back_populates="availabilities")

# backend/models.py

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"

    id = Column(Integer, primary_key=True, index=True)
    # CHANGE THIS LINE: Add nullable=True
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True) 
    
    day = Column(String)
    time_slot = Column(String)

    employee = relationship("Employee", back_populates="assignments")

class ShiftDefinition(Base):
    __tablename__ = "shift_definitions"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String)       # e.g. "MON"
    time_slot = Column(String) # e.g. "10-5"