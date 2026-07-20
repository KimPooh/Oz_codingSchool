from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_medical_user
from app.core.db.databases import async_get_db
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.user import User
from app.schemas.medical_record import MedicalRecordListResponse, MedicalRecordResponse

router = APIRouter(prefix="/api/v1", tags=["medical-records"])
MEDIA_DIR = Path(__file__).resolve().parents[2] / "media" / "xrays"
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


async def active_patient_exists(db: AsyncSession, patient_id: int) -> bool:
    return await db.scalar(select(Patient.id).where(Patient.id == patient_id, Patient.is_deleted.is_(False))) is not None


@router.post("/patients/{patient_id}/medical-records", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    patient_id: int,
    chart_number: str = Form(min_length=1, max_length=50),
    symptoms: str = Form(min_length=1),
    xray_image: UploadFile = File(),
    current_user: User = Depends(require_medical_user),
    db: AsyncSession = Depends(async_get_db),
):
    if not await active_patient_exists(db, patient_id):
        raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")
    suffix = ALLOWED_IMAGE_TYPES.get(xray_image.content_type or "")
    if suffix is None:
        raise HTTPException(status_code=415, detail="JPEG, PNG, WEBP 이미지만 업로드할 수 있습니다.")
    contents = await xray_image.read(MAX_IMAGE_SIZE + 1)
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="X-ray 이미지는 10MB 이하여야 합니다.")
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    path = MEDIA_DIR / filename
    path.write_bytes(contents)
    record = MedicalRecord(
        patient_id=patient_id,
        created_by=current_user.id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image_url=f"/media/xrays/{filename}",
    )
    db.add(record)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="이미 사용 중인 진료 차트 번호입니다.")
    await db.refresh(record)
    return record


@router.get("/patients/{patient_id}/medical-records", response_model=list[MedicalRecordListResponse])
async def list_medical_records(
    patient_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    if not await active_patient_exists(db, patient_id):
        raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")
    result = await db.scalars(
        select(MedicalRecord).where(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.created_at.desc())
    )
    return [
        MedicalRecordListResponse.model_validate(record).model_copy(
            update={"symptoms": f"{record.symptoms[:100]}…" if len(record.symptoms) > 100 else record.symptoms}
        )
        for record in result
    ]


@router.get("/medical-records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    record = await db.scalar(
        select(MedicalRecord)
        .join(Patient)
        .where(MedicalRecord.id == record_id, Patient.is_deleted.is_(False))
    )
    if record is None:
        raise HTTPException(status_code=404, detail="진료기록을 찾을 수 없습니다.")
    return record
