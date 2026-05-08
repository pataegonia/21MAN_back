# Auth API

Base URL: `/api/v1/auth`

---

## POST /api/v1/auth/register

관련 페이지: `pages/01-auth`

회원가입. email, password, username을 받아 계정을 생성한다.

**Endpoint**
```
POST /api/v1/auth/register
```

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| email | string | Y | 사용자 이메일. 중복 불가 | `user@example.com` |
| password | string | Y | 비밀번호. 8자 이상 | `password123!` |
| username | string | Y | 사용자 이름. 영문·숫자·언더스코어, 3~30자. 중복 불가 | `creator123` |

**Request Example**
```json
{
  "email": "user@example.com",
  "password": "password123!",
  "username": "creator123"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 사용자 ID | `1` |
| email | string | Y | 사용자 이메일 | `user@example.com` |
| username | string | Y | 사용자 이름 | `creator123` |
| created_at | string | Y | 계정 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |

**Success Response Example**

201 Created
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "creator123",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response Example**

409 Conflict — 이메일 중복
```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "이미 사용 중인 이메일입니다."
  }
}
```

409 Conflict — username 중복
```json
{
  "error": {
    "code": "USERNAME_ALREADY_EXISTS",
    "message": "이미 사용 중인 username입니다."
  }
}
```

422 Unprocessable Entity — 유효성 검사 실패
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 유효하지 않습니다.",
    "details": [
      { "field": "password", "message": "비밀번호는 8자 이상이어야 합니다." }
    ]
  }
}
```

---

## POST /api/v1/auth/login

관련 페이지: `pages/01-auth`

로그인. email, password를 검증하고 access token과 refresh token을 발급한다.

**Endpoint**
```
POST /api/v1/auth/login
```

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| email | string | Y | 사용자 이메일 | `user@example.com` |
| password | string | Y | 비밀번호 | `password123!` |

**Request Example**
```json
{
  "email": "user@example.com",
  "password": "password123!"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| access_token | string | Y | JWT access token | `eyJhbGci...` |
| refresh_token | string | Y | JWT refresh token | `eyJhbGci...` |
| token_type | string | Y | 토큰 유형 | `Bearer` |

**Success Response Example**

200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Error Response Example**

401 Unauthorized
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "이메일 또는 비밀번호를 확인해주세요."
  }
}
```

---

## POST /api/v1/auth/refresh

관련 페이지: `pages/01-auth`

refresh token으로 새 access token을 발급한다.

**Endpoint**
```
POST /api/v1/auth/refresh
```

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| refresh_token | string | Y | 발급받은 refresh token | `eyJhbGci...` |

**Request Example**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| access_token | string | Y | 새로 발급된 JWT access token | `eyJhbGci...` |
| token_type | string | Y | 토큰 유형 | `Bearer` |

**Success Response Example**

200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Error Response Example**

401 Unauthorized — refresh token 만료 또는 무효
```json
{
  "error": {
    "code": "INVALID_REFRESH_TOKEN",
    "message": "유효하지 않은 refresh token입니다. 다시 로그인해주세요."
  }
}
```

---

## POST /api/v1/auth/logout

관련 페이지: `pages/01-auth`

로그아웃. refresh token을 서버에서 revoke한다.

**Endpoint**
```
POST /api/v1/auth/logout
```

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| refresh_token | string | Y | revoke할 refresh token | `eyJhbGci...` |

**Request Example**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response Body**

(없음)

**Success Response Example**

204 No Content
```
(응답 본문 없음)
```

**Error Response Example**

401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "인증이 필요합니다."
  }
}
```

---

## GET /api/v1/auth/me

관련 페이지: `pages/01-auth`, `pages/14-my-profile`

현재 로그인한 사용자의 정보를 반환한다.

**Endpoint**
```
GET /api/v1/auth/me
```

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 사용자 ID | `1` |
| email | string | Y | 사용자 이메일 | `user@example.com` |
| username | string | Y | 사용자 이름 | `creator123` |
| avatar | string | N | 프로필 이미지 URL | `https://cdn.example.com/avatar.jpg` |
| bio | string | N | 자기소개 | `판타지 세계관을 만드는 작가입니다.` |
| created_at | string | Y | 계정 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "creator123",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "bio": "판타지 세계관을 만드는 작가입니다.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response Example**

401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "인증이 필요합니다."
  }
}
```
