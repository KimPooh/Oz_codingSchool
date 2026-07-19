# 회원 관리 API 명세서

## 1. 공통 사항

- Base URL: `/api/v1`
- 인증 방식: `Authorization: Bearer {access_token}`
- 기본 데이터 형식: `application/json`
- 로그인 요청만 `application/x-www-form-urlencoded`를 사용한다.

## 2. API 목록

| ID | Method | 기능 | Endpoint | 인증 |
| --- | --- | --- | --- | --- |
| REQ-USER-001 | `POST` | 회원가입 | `/users/signup` | - |
| REQ-USER-002 | `POST` | 로그인 | `/users/login` | - |
| REQ-USER-003 | `POST` | 로그아웃 | `/users/logout` | 사용자 |
| REQ-USER-004 | `GET` | 회원 목록 조회 | `/admin/users` | 관리자 |
| REQ-USER-005 | `PATCH` | 회원 권한 변경 | `/admin/users/role` | 관리자 |
| REQ-USER-006 | `GET` | 마이페이지 조회 | `/users/me` | 사용자 |
| REQ-USER-007 | `PATCH` | 회원 정보 수정 | `/users/me` | 사용자 |
| REQ-USER-008 | `PATCH` | 비밀번호 변경 | `/users/me/password` | 사용자 |
| REQ-USER-009 | `DELETE` | 회원 탈퇴 | `/users/me` | 사용자 |

---

## 3. API 상세

### 3.1 회원가입

`POST /api/v1/users/signup`

신규 회원을 등록한다. 가입 직후 권한은 `PENDING`이다.

#### 요청

```json
{
  "email": "example@example.com",
  "password": "Password1!",
  "name": "박강호",
  "department": "DEVELOPMENT",
  "gender": "M",
  "phone_number": "010-1234-5678"
}
```

| 필드 | 필수 | 조건 |
| --- | --- | --- |
| email | Y | 이메일 형식, 중복 불가 |
| password | Y | 8자 이상, 영문·숫자·특수문자 포함 |
| name | Y | 사용자 이름 |
| department | Y | `RESEARCH`, `MEDICAL`, `DEVELOPMENT` |
| gender | Y | `M`, `F` |
| phone_number | Y | `010-XXXX-XXXX` 형식 |

#### 응답

- `201`: 회원 생성 성공 및 회원 정보 반환
- `409`: 이미 가입된 이메일
- `422`: 입력값 검증 실패

> 비밀번호는 Argon2로 해싱하며 응답에 포함하지 않는다.

### 3.2 로그인

`POST /api/v1/users/login`

이메일과 비밀번호를 검증하고 Access Token을 발급한다.

#### 요청

Content-Type: `application/x-www-form-urlencoded`

```text
username=jihyun@example.com
password=Password1234!
```

#### 성공 응답 — `200 OK`

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

- `401`: 이메일 또는 비밀번호 불일치
- `403`: 비활성화된 사용자
- `422`: 필수값 누락 또는 요청 형식 오류

> 화면에서는 이메일을 입력하지만 요청 필드명은 `username`을 사용한다.

### 3.3 로그아웃

`POST /api/v1/users/logout`

- 인증: 필요
- 요청 본문: 없음
- 성공: `204 No Content`
- 실패: `401 Unauthorized`

로그아웃 후 클라이언트에 저장된 Access Token을 삭제한다.

### 3.4 회원 목록 조회

`GET /api/v1/admin/users`

관리자가 회원 목록을 검색·필터링한다.

#### Query Parameters

| 파라미터 | 필수 | 설명 |
| --- | --- | --- |
| keyword | N | 이름 또는 이메일 검색 |
| department | N | 부서 필터 |
| page | N | 페이지 번호 |
| size | N | 페이지 크기 |

#### 성공 응답 — `200 OK`

```json
{
  "users": [
    {
      "id": 1,
      "email": "example@example.com",
      "name": "김오즈",
      "department": "DEVELOPMENT",
      "gender": "M",
      "phone_number": "010-1234-5678",
      "is_active": true
    }
  ]
}
```

- `401`: 인증 실패
- `403`: 관리자 권한 없음

### 3.5 회원 권한 변경

`PATCH /api/v1/admin/users/role`

관리자가 선택한 회원들의 권한을 일괄 변경한다.

#### 요청

```json
{
  "user_ids": [1, 2, 3],
  "new_role": "staff"
}
```

`new_role`은 `pending`, `staff`, `admin` 중 하나다.

#### 성공 응답 — `200 OK`

```json
{
  "updated_count": 3,
  "users": [
    {
      "id": 1,
      "role": "staff"
    }
  ]
}
```

- `403`: 관리자 권한 없음
- `404`: 존재하지 않는 회원 포함
- `422`: 허용되지 않은 권한값

> 현재 관리자 확인에 임시 `X-User-Role: admin` 헤더를 사용하며, JWT 권한 검증 구현 후 제거한다.

### 3.6 마이페이지 조회

`GET /api/v1/users/me`

로그인한 사용자가 자신의 정보를 조회한다.

#### 성공 응답 — `200 OK`

```json
{
  "id": 1,
  "email": "example@example.com",
  "name": "김오즈",
  "department": "DEVELOPMENT",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "USER",
  "is_active": true
}
```

- `401`: 인증 실패
- `404`: 사용자 없음

### 3.7 회원 정보 수정

`PATCH /api/v1/users/me`

부서와 휴대폰 번호를 부분 수정한다.

#### 요청

```json
{
  "department": "RESEARCH",
  "phone_number": "010-1234-1234"
}
```

두 필드는 선택값이지만 최소 하나는 전달해야 한다. 전달하지 않은 값은 기존 값을 유지한다.

- `200`: 수정 성공
- `401`: 인증 실패
- `422`: 수정할 값이 없거나 형식 오류
- `500`: 서버 오류

### 3.8 비밀번호 변경

`PATCH /api/v1/users/me/password`

현재 비밀번호를 확인한 후 새 비밀번호로 변경한다.

#### 요청

```json
{
  "current_password": "CurrentPassword123!",
  "new_password": "NewPassword123!"
}
```

- `200`: 변경 성공
- `400`: 현재 비밀번호 불일치
- `401`: 인증 실패
- `422`: 필수값 누락 또는 형식 오류
- `500`: 서버 오류

> 새 비밀번호는 8자 이상이며 대문자·소문자·숫자·특수문자를 각각 하나 이상 포함해야 한다.

### 3.9 회원 탈퇴

`DELETE /api/v1/users/me`

- 인증: 필요
- 요청 본문: 없음
- `200`: 탈퇴 성공
- `401`: 인증 실패
- `500`: 서버 오류

성공 후 클라이언트에서 로그아웃 처리한다. 실제 삭제와 소프트 삭제 중 어떤 방식을 사용할지는 팀 정책으로 결정한다.

---

## 4. 비기능 요구사항 (Non-Functional Requirements)

### NFR-USER-001 인증 / 인가

#### 설명

- 로그인 성공 시 JWT(JSON Web Token)를 발급하여 API 인증에 사용한다.
- Access Token의 만료 시간은 30분으로 한다.
- Refresh Token의 만료 시간은 7일로 한다.
- Access Token이 만료되면 Refresh Token으로 Access Token을 재발급할 수 있다.
- Refresh Token까지 만료되면 사용자는 다시 로그인해야 한다.
- Refresh Token은 JavaScript에서 접근할 수 없도록 HttpOnly Cookie로 전달한다.
- JWT Payload에는 최소 식별 정보인 `user_id`만 저장한다.

#### 적용 대상

- 로그인 API
- Access Token 재발급 API
- 인증이 필요한 모든 API

### NFR-USER-002 비밀번호 입력 보안

#### 설명

- 모든 비밀번호 입력창은 기본적으로 입력 내용을 마스킹한다.
- 사용자는 비밀번호 보기 아이콘을 눌러 입력한 비밀번호를 확인할 수 있다.
- 비밀번호 입력값이 화면에 평문으로 계속 노출되지 않도록 한다.

#### 적용 대상

- 로그인
- 회원가입
- 비밀번호 변경

### NFR-USER-003 API 성능

#### 설명

- 모든 사용자(User) 관련 API는 요청 후 3초 이내에 응답해야 한다.
- 불필요한 데이터 조회와 중복 로직을 최소화하여 성능을 유지한다.

#### 적용 대상

- 모든 User API
