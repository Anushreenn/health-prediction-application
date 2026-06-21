# from fastapi import FastAPI, Depends, HTTPException, Request, Form
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.orm import Session
# from datetime import date

# from app import models, schemas, services
# from app.database import engine, get_db, Base  # Imported Base directly from database

# # Create DB Tables safely using the base declaration directly
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="AI Health Management Portal")
# templates = Jinja2Templates(directory="templates")

# # Dashboard - READ ALL
# @app.get("/", response_class=HTMLResponse)
# def read_root(request: Request, db: Session = Depends(get_db)):
#     patients = db.query(models.Patient).all()
#     return templates.TemplateResponse("index.html", {"request": request, "patients": patients})

# # CREATE Operation
# @app.post("/patient/add")
# def create_patient(
#     full_name: str = Form(...),
#     dob: str = Form(...),
#     email: str = Form(...),
#     glucose: float = Form(...),
#     haemoglobin: float = Form(...),
#     cholesterol: float = Form(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Validate data with Pydantic
#         patient_data = schemas.PatientCreate(
#             full_name=full_name,
#             dob=date.fromisoformat(dob),
#             email=email,
#             glucose=glucose,
#             haemoglobin=haemoglobin,
#             cholesterol=cholesterol
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     # Generate AI prediction remarks
#     ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)

#     db_patient = models.Patient(
#         full_name=patient_data.full_name,
#         dob=patient_data.dob,
#         email=patient_data.email,
#         glucose=patient_data.glucose,
#         haemoglobin=patient_data.haemoglobin,
#         cholesterol=patient_data.cholesterol,
#         remarks=ai_remarks
#     )
#     db.add(db_patient)
#     db.commit()
#     return RedirectResponse(url="/", status_code=303)

# # UPDATE Operation
# @app.post("/patient/update/{patient_id}")
# def update_patient(
#     patient_id: int,
#     full_name: str = Form(...),
#     dob: str = Form(...),
#     email: str = Form(...),
#     glucose: float = Form(...),
#     haemoglobin: float = Form(...),
#     cholesterol: float = Form(...),
#     db: Session = Depends(get_db)
# ):
#     db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
#     if not db_patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     # Re-trigger AI analysis if clinical numbers changed
#     if (db_patient.glucose != glucose or 
#         db_patient.haemoglobin != haemoglobin or 
#         db_patient.cholesterol != cholesterol):
#         ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)
#     else:
#         ai_remarks = db_patient.remarks

#     db_patient.full_name = full_name
#     db_patient.dob = date.fromisoformat(dob)
#     db_patient.email = email
#     db_patient.glucose = glucose
#     db_patient.haemoglobin = haemoglobin
#     db_patient.cholesterol = cholesterol
#     db_patient.remarks = ai_remarks

#     db.commit()
#     return RedirectResponse(url="/", status_code=303)

# # DELETE Operation
# @app.get("/patient/delete/{patient_id}")
# def delete_patient(patient_id: int, db: Session = Depends(get_db)):
#     db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
#     if db_patient:
#         db.delete(db_patient)
#         db.commit()
#     return RedirectResponse(url="/", status_code=303)




from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app import models, schemas, services
from app.database import engine, get_db, Base 

# Create DB Tables safely using the base declaration directly
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Health Management Portal")
templates = Jinja2Templates(directory="templates")

# Dashboard - READ ALL
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return templates.TemplateResponse("index.html", {"request": request, "patients": patients})

# CREATE Operation
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
        # Validate data with Pydantic
        patient_data = schemas.PatientCreate(
            full_name=full_name,
            dob=date.fromisoformat(dob),
            email=email,
            glucose=glucose,
            haemoglobin=haemoglobin,
            cholesterol=cholesterol
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate AI prediction remarks
    ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)

    # Maps validated schemas cleanly onto updated models properties
    db_patient = models.Patient(
        name=patient_data.full_name,  
        dob=patient_data.dob,
        email=patient_data.email,
        glucose=patient_data.glucose,
        haemoglobin=patient_data.haemoglobin,
        cholesterol=patient_data.cholesterol,
        remarks=ai_remarks
    )
    db.add(db_patient)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

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
        raise HTTPException(status_code=404, detail="Patient not found")

    # Re-trigger AI analysis if clinical numbers changed
    if (db_patient.glucose != glucose or 
        db_patient.haemoglobin != haemoglobin or 
        db_patient.cholesterol != cholesterol):
        ai_remarks = services.generate_health_remarks(glucose, haemoglobin, cholesterol)
    else:
        ai_remarks = db_patient.remarks

    # Safe updates utilizing matching column identifiers
    db_patient.name = full_name
    db_patient.dob = date.fromisoformat(dob)
    db_patient.email = email
    db_patient.glucose = glucose
    db_patient.haemoglobin = haemoglobin
    db_patient.cholesterol = cholesterol
    db_patient.remarks = ai_remarks

    db.commit()
    return RedirectResponse(url="/", status_code=303)

# DELETE Operation
@app.get("/patient/delete/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
    return RedirectResponse(url="/", status_code=303)