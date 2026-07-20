# 환자 관리 및 진료기록 API 설계

- 요구사항: `REQ-PTNT-001` ~ `REQ-PTNT-005`, `REQ-MDR-001` ~ `REQ-MDR-003`
- 기본 경로: `/api/v1`
- 인증: `Authorization: Bearer {access_token}` 필수
- 공통 오류: `401` 인증 실패, `404` 리소스 없음, `422` 입력값 검증 실패

## 환자 API

| 요구사항 | Method | Endpoint | 설명 | 성공 응답 |
| --- | --- | --- | --- | --- |
| REQ-PTNT-001 | `POST` | `/patients` | 이름, 나이, 성별, 연락처로 환자 등록 | `201` 환자 정보 |
| REQ-PTNT-002 | `GET` | `/patients` | 환자 목록과 이름 검색, 성별·나이 범위 필터 | `200` 환자 목록 |
| REQ-PTNT-003 | `GET` | `/patients/{patient_id}` | 환자 상세 조회 | `200` 환자 정보 |
| REQ-PTNT-004 | `PATCH` | `/patients/{patient_id}` | 이름 또는 연락처 수정 | `200` 수정된 정보 |
| REQ-PTNT-005 | `DELETE` | `/patients/{patient_id}` | 환자와 진료기록·X-ray 파일 삭제 | `204` |

### 환자 등록 요청

```json
{
  "name": "홍길동",
  "age": 42,
  "gender": "male",
  "phone_number": "010-1234-5678"
}
```

성별은 `male`, `female` 중 하나이며 나이는 0~150, 연락처는 국내 휴대폰 번호 형식이어야 한다.

### 환자 목록 Query Parameters

| 이름 | 형식 | 설명 |
| --- | --- | --- |
| `name` | string | 이름 부분 검색 |
| `gender` | `male` 또는 `female` | 성별 필터 |
| `min_age` | integer | 최소 나이 |
| `max_age` | integer | 최대 나이 |
| `offset` | integer | 건너뛸 개수, 기본값 0 |
| `limit` | integer | 조회 개수, 기본값 20, 최대 100 |

## 진료기록 API

| 요구사항 | Method | Endpoint | 설명 | 성공 응답 |
| --- | --- | --- | --- | --- |
| REQ-MDR-001 | `POST` | `/patients/{patient_id}/medical-records` | X-ray 이미지를 포함한 진료기록 등록 | `201` 진료기록 |
| REQ-MDR-002 | `GET` | `/patients/{patient_id}/medical-records` | 환자별 진료기록 목록 조회 | `200` 진료기록 목록 |
| REQ-MDR-003 | `GET` | `/medical-records/{record_id}` | 진료기록 상세 조회 | `200` 진료기록 |

### 진료기록 등록 요청

`multipart/form-data`를 사용한다.

| 필드 | 형식 | 필수 | 규칙 |
| --- | --- | --- | --- |
| `chart_number` | string | Y | 최대 50자, 전체 시스템에서 고유 |
| `symptoms` | string | Y | 진료된 증상 |
| `xray_image` | file | Y | JPEG, PNG, WEBP, 최대 10MB |

파일은 서버의 `media/xrays`에 임의 파일명으로 저장하고 `/media/xrays/{파일명}` URL을 응답한다. 목록 응답에서는 증상이 100자를 초과하면 100자 뒤에 `…`를 붙이며, 상세 응답에서는 전체 증상을 제공한다.

## 주요 오류 응답

| 상태 | 상황 |
| --- | --- |
| `400` | 최소 나이가 최대 나이보다 큼 |
| `401` | 토큰 누락, 만료, 변조 또는 로그아웃된 토큰 |
| `404` | 환자 또는 진료기록 없음 |
| `409` | 진료 차트 번호 중복 |
| `413` | 이미지가 10MB 초과 |
| `415` | 지원하지 않는 이미지 형식 |
| `422` | 필수값 누락 또는 형식 오류 |

## Swagger-UI 테스트 순서

1. `POST /api/v1/users/login`에서 이메일을 `username` 필드에 입력해 토큰을 발급받는다.
2. Swagger 상단 **Authorize**에 발급받은 토큰을 입력한다.
3. 환자 등록 → 목록/상세 → 수정 순서로 호출한다.
4. 진료기록 등록에서 X-ray 파일을 첨부한 뒤 목록과 상세를 호출한다.
5. 환자를 삭제하고 환자·진료기록 상세가 모두 `404`인지 확인한다.

모든 API는 3초 이내 응답을 목표로 하며 이름·성별·환자 ID·차트 번호에 설정된 DB 인덱스를 활용한다.
