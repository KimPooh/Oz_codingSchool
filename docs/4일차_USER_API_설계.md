# User API 설계 - 로그인 및 로그아웃

- 담당자: 김지현
- 담당 기능: 로그인, 로그아웃
- 요구사항 ID: `REQ-USER-002`, `REQ-USER-003`

## 1. 로그인

### 기본 정보

| 구분 | 내용 |
| --- | --- |
| 요구사항 ID | `REQ-USER-002` |
| 기능 | 가입된 이메일과 비밀번호를 이용한 로그인 |
| HTTP Method | `POST` |
| Endpoint | `/api/v1/users/login` |
| 인증 필요 여부 | 불필요 |
| Content-Type | `application/x-www-form-urlencoded` |

### 기능 설명

사용자가 회원가입 시 등록한 이메일과 비밀번호로 로그인합니다. 서버는 이메일에 해당하는 사용자를 조회하고 암호화된 비밀번호를 검증합니다. 인증에 성공하면 이후 API 인증에 사용할 Access Token을 반환합니다.

이메일이 존재하지 않는 경우와 비밀번호가 일치하지 않는 경우에는 계정 존재 여부가 노출되지 않도록 동일한 오류 메시지를 반환합니다.

### 요청 데이터

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `username` | string | Y | 회원가입 시 등록한 이메일 |
| `password` | string | Y | 회원가입 시 등록한 비밀번호 |

화면에서는 이메일을 입력하지만 인증 Form 형식에 맞춰 요청 필드명은 `username`을 사용합니다.

### 요청 예시

```text
username=jihyun@example.com
password=Password1234!
```

### 성공 응답

#### `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `access_token` | string | API 인증에 사용하는 Access Token |
| `token_type` | string | 토큰 인증 방식. `bearer`로 반환 |

### 실패 응답

#### `401 Unauthorized`

이메일이 존재하지 않거나 비밀번호가 일치하지 않는 경우입니다.

```json
{
  "detail": "이메일 또는 비밀번호가 올바르지 않습니다."
}
```

#### `403 Forbidden`

탈퇴 또는 비활성화된 사용자가 로그인을 시도한 경우입니다.

```json
{
  "detail": "비활성화된 사용자입니다."
}
```

#### `422 Unprocessable Entity`

이메일 또는 비밀번호가 누락되었거나 요청 형식이 올바르지 않은 경우입니다.

## 2. 로그아웃

### 기본 정보

| 구분 | 내용 |
| --- | --- |
| 요구사항 ID | `REQ-USER-003` |
| 기능 | 로그인된 사용자의 로그아웃 |
| HTTP Method | `POST` |
| Endpoint | `/api/v1/users/logout` |
| 인증 필요 여부 | 필요 |

### 기능 설명

현재 로그인된 사용자를 로그아웃 처리합니다. 로그아웃에 성공하면 클라이언트에 저장된 Access Token을 삭제합니다. 서버가 인증 토큰을 쿠키로 관리하는 경우 해당 쿠키도 삭제합니다.

### 요청 헤더

| 헤더 | 필수 | 설명 |
| --- | --- | --- |
| `Authorization` | Y | `Bearer {access_token}` 형식의 인증 정보 |

별도의 요청 본문은 사용하지 않습니다.

### 요청 예시

```http
POST /api/v1/users/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 성공 응답

#### `204 No Content`

로그아웃에 성공하면 응답 본문을 반환하지 않습니다.

### 실패 응답

#### `401 Unauthorized`

Authorization 헤더가 없거나 Access Token이 유효하지 않은 경우입니다.

```json
{
  "detail": "인증 정보가 없거나 유효하지 않습니다."
}
```

## 공통 보안 요구사항

- 비밀번호 원문을 데이터베이스에 저장하지 않습니다.
- 회원가입과 로그인에서 동일한 비밀번호 해싱 방식을 사용합니다.
- 로그인 실패 시 이메일 존재 여부를 구분할 수 없도록 동일한 메시지를 반환합니다.
- Access Token에는 비밀번호와 같은 민감한 정보를 포함하지 않습니다.
- 실제 배포 환경의 인증 API는 HTTPS를 사용합니다.
- 로그아웃 성공 후 클라이언트에 저장된 Access Token을 삭제합니다.

## 팀 확인 필요 사항

- Access Token 유효기간
- Refresh Token 사용 여부
- 비밀번호 해싱 라이브러리와 알고리즘
- 로그아웃 시 서버에서 토큰을 무효화할지 여부
- 오류 응답의 공통 형식
