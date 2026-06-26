from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime

from app import models, schemas, services
from app.database import engine, get_db, Base 

# Create DB Tables safely using the base declaration directly
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Health Management Portal")
templates = Jinja2Templates(directory="templates")

# Dashboard - READ ALL (Formats dates neatly for India/Australia locale display)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    raw_patients = db.query(models.Patient).all()
    
    # Process patients list to structure date format natively to DD/MM/YYYY
    formatted_patients = []
    for p in raw_patients:
        # Format for table view (India/UK locale standard)
        display_dob = p.dob.strftime("%d/%m/%Y") if isinstance(p.dob, (date, datetime)) else str(p.dob)
        
        # Format explicitly as a string for HTML <input type="date"> value matching (YYYY-MM-DD)
        input_ready_dob = p.dob.strftime("%Y-%m-%d") if isinstance(p.dob, (date, datetime)) else str(p.dob)
        
        # Build a temporary dictionary safe for Jinja template looping
        formatted_patients.append({
            "id": p.id,
            "name": p.name,
            "dob": display_dob,
            "raw_dob": input_ready_dob,  # Fixed: Passes string layout matching HTML requirements
            "email": p.email,
            "glucose": p.glucose,
            "haemoglobin": p.haemoglobin,
            "cholesterol": p.cholesterol,
            "remarks": p.remarks
        })
        
    return templates.TemplateResponse("index.html", {"request": request, "patients": formatted_patients})

# CREATE Operation (Asynchronous UI Form Friendly)
@app.post("/patient/add")
def create_patient(
    full_name: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    glucose: float = Form(...),
    haemoglobin: float = Form(...),
    cholesterol: float = Form(...),
    db: Session = Depends(get_db)
):
    try:
        input_date = date.fromisoformat(dob)
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Inverted or malformed calendar date layout calculation."})

    # Strict Validation Rule: Date cannot be in the future
    if input_date > date.today():
        return JSONResponse(
            status_code=400, 
            content={"detail": "Registration error: Date of Birth cannot be in the future."}
        )

    try:
        # Validate data structure through Pydantic
        patient_data = schemas.PatientCreate(
            full_name=full_name,
            dob=input_date,
            email=email,
            glucose=glucose,
            haemoglobin=haemoglobin,
            cholesterol=cholesterol
        )
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

    # Generate AI prediction remarks 
    ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)

    db_patient = models.Patient(
        name=patient_data.full_name,  
        dob=patient_data.dob,
        email=patient_data.email,
        glucose=patient_data.glucose,
        haemoglobin=patient_data.haemoglobin,
        cholesterol=patient_data.cholesterol,
        remarks=ai_remarks
    )
    
    try:
        db.add(db_patient)
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=400, 
            content={"detail": "A record database profile with this email address already exists."}
        )
        
    return JSONResponse(status_code=200, content={"message": "Patient entry completed successfully."})

# UPDATE Operation
@app.post("/patient/update/{patient_id}")
def update_patient(
    patient_id: int,
    full_name: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    glucose: float = Form(...),
    haemoglobin: float = Form(...),
    cholesterol: float = Form(...),
    db: Session = Depends(get_db)
):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        return JSONResponse(status_code=404, content={"detail": "Patient entity not tracked within table."})

    try:
        input_date = date.fromisoformat(dob)
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Inverted calendar layout configuration."})

    if input_date > date.today():
        return JSONResponse(status_code=400, content={"detail": "Registration error: Date of Birth cannot be in the future."})

    # Re-trigger AI analysis if clinical numbers changed
    if (db_patient.glucose != glucose or 
        db_patient.haemoglobin != haemoglobin or 
        db_patient.cholesterol != cholesterol):
        ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)
    else:
        ai_remarks = db_patient.remarks

    db_patient.name = full_name
    db_patient.dob = input_date
    db_patient.email = email
    db_patient.glucose = glucose
    db_patient.haemoglobin = haemoglobin
    db_patient.cholesterol = cholesterol
    db_patient.remarks = ai_remarks

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return JSONResponse(status_code=400, content={"detail": "A record database profile with this email address already exists."})
        
    return JSONResponse(status_code=200, content={"message": "Patient profile successfully tracked and saved."})

# DELETE Operation (Synchronous anchor-tag interaction friendly)
@app.get("/patient/delete/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

