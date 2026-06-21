from sqlalchemy import Column, Integer, String, Float, Text, Date
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)
    email = Column(String, unique=True, index=True)
    glucose = Column(Float)
    haemoglobin = Column(Float)
    cholesterol = Column(Float)
    remarks = Column(Text)