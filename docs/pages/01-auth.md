# 01 — 인증 (회원가입 / 로그인 / 로그아웃)

## 개요

사용자 계정 생성, 로그인, 토큰 갱신, 로그아웃, 현재 사용자 정보 조회를 처리하는 인증 흐름이다.

---

## 접근 권한

| 화면 | 권한 |
|------|------|
| 회원가입 | 🌐 누구나 |
| 로그인 | 🌐 누구나 |
| 로그아웃 | 🔑 로그인 사용자 |
| 내 정보 조회 | 🔑 로그인 사용자 |

---

## 화면 구성요소

### 회원가입 폼
- 이메일 입력 필드
- 비밀번호 입력 필드
- username 입력 필드
- 제출 버튼
- 로그인 페이지 링크

### 로그인 폼
- 이메일 입력 필드
- 비밀번호 입력 필드
- 제출 버튼
- 회원가입 페이지 링크

---

## 사용자 액션

| 액션 | 설명 |
|------|------|
| 회원가입 | email, password, username 입력 후 계정 생성 |
| 로그인 | email, password 입력 후 access/refresh 토큰 발급 |
| 로그아웃 | refresh token revoke, 클라이언트 토큰 삭제 |
| 토큰 갱신 | access token 만료 시 refresh token으로 재발급 (자동) |

---

## API 연동

### POST /api/v1/auth/register
```
Request:
{
  "email": "string",
  "password": "string",
  "username": "string"
}

Response 201:
{
  "id": 1,
  "email": "...",
  "username": "...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /api/v1/auth/login
```
Request:
{
  "email": "string",
  "password": "string"
}

Response 200:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer"
}
```

### POST /api/v1/auth/refresh
```
Request:
{
  "refresh_token": "..."
}

Response 200:
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

### POST /api/v1/auth/logout
```
Header: Authorization: Bearer {access_token}
Request:
{
  "refresh_token": "..."
}

Response 204: (no content)
```

### GET /api/v1/auth/me
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "id": 1,
  "email": "...",
  "username": "...",
  "avatar": "...",
  "bio": "...",
  "created_at": "..."
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 이메일 중복 | 409 Conflict — "이미 사용 중인 이메일입니다" |
| username 중복 | 409 Conflict — "이미 사용 중인 username입니다" |
| 잘못된 비밀번호 | 401 Unauthorized — "이메일 또는 비밀번호를 확인해주세요" |
| access token 만료 | 401 → 자동으로 refresh 시도 |
| refresh token 만료 | 401 → 로그인 페이지로 리다이렉트 |

---

## 규칙 및 제약

- username은 영문·숫자·언더스코어만 허용, 3~30자
- 비밀번호는 8자 이상
- access token 유효기간: 단기 (예: 1시간)
- refresh token 유효기간: 장기 (예: 30일)
- 로그아웃 시 서버에서 refresh token을 revoke해야 함 (재사용 방지)
- 인증이 필요한 모든 엔드포인트는 `Authorization: Bearer {access_token}` 헤더 필수

---

## 연결 화면

- 회원가입 성공 → 로그인 페이지 또는 자동 로그인 후 홈
- 로그인 성공 → 직전 페이지 또는 홈
- 로그아웃 → 홈
