import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.user import Gender

PHONE_PATTERN = re.compile(r"^01[016789]-?\d{3,4}-?\d{4}$")


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    gender: Gender
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("휴대폰 번호 형식이 올바르지 않습니다.")
        return value


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    phone_number: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is not None and not PHONE_PATTERN.fullmatch(value):
            raise ValueError("휴대폰 번호 형식이 올바르지 않습니다.")
        return value

    @model_validator(mode="after")
    def require_update_field(self):
        if self.name is None and self.phone_number is None:
            raise ValueError("수정할 이름 또는 연락처가 필요합니다.")
        return self


class PatientResponse(PatientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime | None
