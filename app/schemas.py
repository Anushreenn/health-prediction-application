from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

class PatientBase(BaseModel):
    full_name: str
    dob: date
    email: EmailStr
    glucose: float
    haemoglobin: float
    cholesterol: float

    @field_validator('dob')
    @classmethod
    def dob_cannot_be_future(cls, v):
        if v > date.today():
            raise ValueError('Date of Birth cannot be a future date.')
        return v

    @field_validator('glucose', 'haemoglobin', 'cholesterol')
    @classmethod
    def values_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Health metrics must be greater than zero.')
        return v

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    remarks: str

    class Config:
        from_attributes = True