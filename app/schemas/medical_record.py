from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: str
    created_at: datetime
    updated_at: datetime | None


class MedicalRecordListResponse(MedicalRecordResponse):
    pass
