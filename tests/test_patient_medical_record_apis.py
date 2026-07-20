from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.apis import medical_record_apis
from app.core.auth import hash_password, revoked_tokens
from app.core.db.databases import Base, async_get_db
from app.main import app
from app.models import User
from app.models.user import Department, Gender, UserRole


@pytest.fixture()
def client(tmp_path: Path):
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def prepare_database():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            session.add(
                User(
                    email="doctor@example.com",
                    password=hash_password("Password1234!"),
                    name="의사",
                    department=Department.MEDICAL_TEAM,
                    gender=Gender.FEMALE,
                    phone_number="010-1111-2222",
                    role=UserRole.STAFF,
                    is_active=True,
                )
            )
            await session.commit()

    async def override_db():
        async with session_factory() as session:
            yield session

    import asyncio
    asyncio.run(prepare_database())
    app.dependency_overrides[async_get_db] = override_db
    revoked_tokens.clear()
    original_media_dir = medical_record_apis.MEDIA_DIR
    medical_record_apis.MEDIA_DIR = tmp_path / "xrays"
    with TestClient(app) as test_client:
        yield test_client
    medical_record_apis.MEDIA_DIR = original_media_dir
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


def authorization(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/users/login",
        data={"username": "doctor@example.com", "password": "Password1234!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_patient_and_medical_record_flow(client: TestClient):
    headers = authorization(client)
    created = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"name": "홍길동", "age": 42, "gender": "male", "phone_number": "010-1234-5678"},
    )
    assert created.status_code == 201
    patient_id = created.json()["id"]

    listed = client.get("/api/v1/patients?name=홍&gender=male&min_age=40&max_age=45", headers=headers)
    assert listed.status_code == 200
    assert [patient["id"] for patient in listed.json()] == [patient_id]

    updated = client.patch(
        f"/api/v1/patients/{patient_id}", headers=headers, json={"name": "홍길순"}
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "홍길순"

    record = client.post(
        f"/api/v1/patients/{patient_id}/medical-records",
        headers=headers,
        data={"chart_number": "CHART-001", "symptoms": "기침" * 60},
        files={"xray_image": ("xray.png", b"fake-png", "image/png")},
    )
    assert record.status_code == 201
    record_id = record.json()["id"]

    records = client.get(f"/api/v1/patients/{patient_id}/medical-records", headers=headers)
    assert records.status_code == 200
    assert records.json()[0]["symptoms"].endswith("…")
    assert len(records.json()[0]["symptoms"]) == 101

    detail = client.get(f"/api/v1/medical-records/{record_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["symptoms"]) == 120

    deleted = client.delete(f"/api/v1/patients/{patient_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/patients/{patient_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/medical-records/{record_id}", headers=headers).status_code == 404


def test_authentication_and_validation(client: TestClient):
    assert client.get("/docs").status_code == 200
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "/api/v1/patients" in openapi.json()["paths"]
    assert "/api/v1/patients/{patient_id}/medical-records" in openapi.json()["paths"]
    assert client.get("/api/v1/patients").status_code == 401
    headers = authorization(client)
    invalid = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"name": "환자", "age": 151, "gender": "male", "phone_number": "123"},
    )
    assert invalid.status_code == 422
    logout = client.post("/api/v1/users/logout", headers=headers)
    assert logout.status_code == 204
    assert client.get("/api/v1/patients", headers=headers).status_code == 401
