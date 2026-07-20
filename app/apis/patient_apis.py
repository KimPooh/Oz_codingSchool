from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_user, require_medical_user
from app.core.db.databases import async_get_db
from app.models.patient import Patient
from app.models.user import Gender, User
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(prefix="/api/v1/patients", tags=["patients"], dependencies=[Depends(get_current_user)])


async def get_patient_or_404(db: AsyncSession, patient_id: int, *, with_records: bool = False) -> Patient:
    statement = select(Patient).where(Patient.id == patient_id, Patient.is_deleted.is_(False))
    if with_records:
        statement = statement.options(selectinload(Patient.medical_records))
    patient = await db.scalar(statement)
    if patient is None:
        raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")
    return patient


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    _: User = Depends(require_medical_user),
    db: AsyncSession = Depends(async_get_db),
):
    patient = Patient(**payload.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientResponse])
async def list_patients(
    name: str | None = Query(default=None, max_length=50),
    gender: Gender | None = None,
    min_age: int | None = Query(default=None, ge=0, le=150),
    max_age: int | None = Query(default=None, ge=0, le=150),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(async_get_db),
):
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(status_code=400, detail="최소 나이는 최대 나이보다 클 수 없습니다.")
    statement = select(Patient).where(Patient.is_deleted.is_(False))
    if name:
        statement = statement.where(Patient.name.contains(name))
    if gender:
        statement = statement.where(Patient.gender == gender)
    if min_age is not None:
        statement = statement.where(Patient.age >= min_age)
    if max_age is not None:
        statement = statement.where(Patient.age <= max_age)
    result = await db.scalars(statement.order_by(Patient.id.desc()).offset(offset).limit(limit))
    return list(result)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    return await get_patient_or_404(db, patient_id)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, payload: PatientUpdate, db: AsyncSession = Depends(async_get_db)):
    patient = await get_patient_or_404(db, patient_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    patient = await get_patient_or_404(db, patient_id, with_records=True)
    for record in patient.medical_records:
        if record.xray_image_url.startswith("/media/"):
            media_path = Path(__file__).resolve().parents[2] / record.xray_image_url.removeprefix("/media/")
            media_path.unlink(missing_ok=True)
        await db.delete(record)
    patient.is_deleted = True
    patient.deleted_at = datetime.now(UTC)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
