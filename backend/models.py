from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    symptoms = Column(String)
    heart_rate = Column(Float)
    oxygen = Column(Float)
    glucose = Column(Float)
    diagnosis = Column(String)
    risk_level = Column(String)
    emergency = Column(Boolean)