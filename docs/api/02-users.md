# Users API

Base URL: `/api/v1/users`

---

## GET /api/v1/users/{username}

관련 페이지: `pages/13-user-profile`

사용자의 공개 프로필 기본 정보를 반환한다.

**Endpoint**
```
GET /api/v1/users/{username}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `creator123` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/creator123
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 사용자 ID | `1` |
| username | string | Y | 사용자 이름 | `creator123` |
| avatar | string | N | 프로필 이미지 URL | `https://cdn.example.com/avatar.jpg` |
| bio | string | N | 자기소개 | `판타지 세계관을 만드는 작가입니다.` |
| created_at | string | Y | 계정 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 1,
  "username": "creator123",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "bio": "판타지 세계관을 만드는 작가입니다.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/repositories

관련 페이지: `pages/13-user-profile`

사용자가 생성한 Repository 목록을 반환한다.

**Endpoint**
```
GET /api/v1/users/{username}/repositories
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `creator123` |

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/creator123/repositories?page=1&size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | Repository 목록 | `[...]` |
| items[].id | integer | Y | Repository ID | `1` |
| items[].title | string | Y | 작품 제목 | `내 판타지 세계관` |
| items[].thumbnail | string | N | 썸네일 URL | `https://cdn.example.com/thumb.jpg` |
| items[].tags | array | Y | 태그 목록 | `["판타지", "마법"]` |
| items[].merge_count | integer | Y | Merge된 기여 수 | `5` |
| items[].pr_count | integer | Y | 전체 PR 수 | `12` |
| items[].created_at | string | Y | 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |
| total | integer | Y | 전체 결과 수 | `3` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "id": 1,
      "title": "내 판타지 세계관",
      "thumbnail": "https://cdn.example.com/thumb.jpg",
      "tags": ["판타지", "마법"],
      "merge_count": 5,
      "pr_count": 12,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 3,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/contributions

관련 페이지: `pages/13-user-profile`

사용자가 Merge된 기여 목록을 반환한다.

**Endpoint**
```
GET /api/v1/users/{username}/contributions
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `contributor123` |

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| grade | string | N | 등급 필터 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/contributor123/contributions?grade=MAJOR&page=1&size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | 기여 목록 | `[...]` |
| items[].merge_id | integer | Y | Merge ID | `5` |
| items[].pull_request | object | Y | 관련 PR 정보 | `{...}` |
| items[].pull_request.id | integer | Y | PR ID | `42` |
| items[].pull_request.title | string | Y | PR 제목 | `마법사 아르카의 숨겨진 과거` |
| items[].repository | object | Y | 대상 Repository 정보 | `{...}` |
| items[].repository.id | integer | Y | Repository ID | `1` |
| items[].repository.title | string | Y | Repository 제목 | `내 판타지 세계관` |
| items[].final_grade | string | Y | 최종 등급 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| items[].merged_at | string | Y | 병합 시각 (ISO 8601 UTC) | `2024-01-03T12:00:00Z` |
| total | integer | Y | 전체 결과 수 | `10` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "merge_id": 5,
      "pull_request": {
        "id": 42,
        "title": "마법사 아르카의 숨겨진 과거"
      },
      "repository": {
        "id": 1,
        "title": "내 판타지 세계관"
      },
      "final_grade": "MAJOR",
      "merged_at": "2024-01-03T12:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/pull-requests

관련 페이지: `pages/13-user-profile`, `pages/14-my-profile`

사용자의 PR 목록을 반환한다. 본인이면 전체(PRIVATE, DRAFT 포함), 타인이면 PUBLIC + DRAFT 제외만 반환한다.

**Endpoint**
```
GET /api/v1/users/{username}/pull-requests
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `contributor123` |

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| status | string | N | 상태 필터. 반복 가능 (`DRAFT`, `SUBMITTED`, `ACCEPTED`, `CHANGES_REQUESTED`, `REJECTED`, `MERGED`) | `SUBMITTED` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | N | Bearer access token. 본인 조회 시 전체 반환을 위해 필요 | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/contributor123/pull-requests?status=DRAFT&status=SUBMITTED&page=1&size=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | PR 목록 | `[...]` |
| items[].id | integer | Y | PR ID | `42` |
| items[].repository | object | Y | 대상 Repository 정보 | `{...}` |
| items[].repository.id | integer | Y | Repository ID | `1` |
| items[].repository.title | string | Y | Repository 제목 | `내 판타지 세계관` |
| items[].title | string | N | PR 제목 (AI 생성, 분석 전이면 null) | `마법사 아르카의 숨겨진 과거` |
| items[].status | string | Y | PR 상태 | `SUBMITTED` |
| items[].visibility | string | Y | 공개 여부 (`PUBLIC`, `PRIVATE`) | `PUBLIC` |
| items[].ai_grade | string | N | AI 판정 등급 | `MAJOR` |
| items[].author_grade_override | string | N | 원작자 확정 등급 | `NORMAL` |
| items[].first_drafted_at | string | Y | 첫 작성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00.000000Z` |
| items[].last_saved_at | string | Y | 마지막 저장 시각 | `2024-01-01T00:05:00.000000Z` |
| items[].submitted_at | string | N | 제출 시각 | `2024-01-01T01:00:00.000000Z` |
| total | integer | Y | 전체 결과 수 | `15` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "id": 42,
      "repository": {
        "id": 1,
        "title": "내 판타지 세계관"
      },
      "title": "마법사 아르카의 숨겨진 과거",
      "status": "SUBMITTED",
      "visibility": "PUBLIC",
      "ai_grade": "MAJOR",
      "author_grade_override": null,
      "first_drafted_at": "2024-01-01T00:00:00.000000Z",
      "last_saved_at": "2024-01-01T00:55:00.000000Z",
      "submitted_at": "2024-01-01T01:00:00.000000Z"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/stats/contributor

관련 페이지: `pages/13-user-profile`

사용자의 컨트리뷰터 통계를 반환한다. on-demand 집계 쿼리로 계산한다.

**Endpoint**
```
GET /api/v1/users/{username}/stats/contributor
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `contributor123` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/contributor123/stats/contributor
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| total_prs | integer | Y | 제출한 전체 PR 수 (DRAFT 제외) | `15` |
| merged_prs | integer | Y | Merge된 PR 수 | `8` |
| major_count | integer | Y | MAJOR 등급 Merge 수 | `2` |
| normal_count | integer | Y | NORMAL 등급 Merge 수 | `4` |
| minor_count | integer | Y | MINOR 등급 Merge 수 | `2` |
| merge_ratio | number | Y | Merge 비율 (0.00~1.00) | `0.53` |
| last_activity_at | string | N | 마지막 활동 시각 (ISO 8601 UTC) | `2024-06-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "total_prs": 15,
  "merged_prs": 8,
  "major_count": 2,
  "normal_count": 4,
  "minor_count": 2,
  "merge_ratio": 0.53,
  "last_activity_at": "2024-06-01T00:00:00Z"
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/stats/author

관련 페이지: `pages/13-user-profile`

사용자의 원작자 통계를 반환한다. on-demand 집계 쿼리로 계산한다.

**Endpoint**
```
GET /api/v1/users/{username}/stats/author
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `creator123` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/creator123/stats/author
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repository_count | integer | Y | 생성한 Repository 수 | `3` |
| received_prs | integer | Y | 받은 전체 PR 수 (DRAFT 제외) | `25` |
| merged_prs | integer | Y | Merge한 PR 수 | `12` |
| merge_ratio | number | Y | Merge 비율 (0.00~1.00) | `0.48` |
| avg_review_days | number | Y | 평균 검토 기간 (일 단위) | `2.5` |
| last_activity_at | string | N | 마지막 활동 시각 (ISO 8601 UTC) | `2024-06-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "repository_count": 3,
  "received_prs": 25,
  "merged_prs": 12,
  "merge_ratio": 0.48,
  "avg_review_days": 2.5,
  "last_activity_at": "2024-06-01T00:00:00Z"
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## GET /api/v1/users/{username}/badges

관련 페이지: `pages/13-user-profile`

사용자의 뱃지 목록을 반환한다. MVP에서는 빈 배열을 반환해도 된다.

**Endpoint**
```
GET /api/v1/users/{username}/badges
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 조회할 사용자의 username | `creator123` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/users/creator123/badges
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| badges | array | Y | 뱃지 목록. MVP에서는 빈 배열 가능 | `[]` |
| badges[].id | string | Y | 뱃지 식별자 | `first_merge` |
| badges[].name | string | Y | 뱃지 이름 | `첫 Merge` |
| badges[].description | string | Y | 뱃지 획득 조건 설명 | `첫 번째 기여가 Merge되었습니다.` |
| badges[].earned_at | string | Y | 획득 시각 (ISO 8601 UTC) | `2024-01-03T12:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "badges": []
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "존재하지 않는 사용자입니다."
  }
}
```

---

## PATCH /api/v1/users/{username}

관련 페이지: `pages/14-my-profile`

본인의 프로필(아바타, bio)을 수정한다. 본인만 호출 가능하다.

**Endpoint**
```
PATCH /api/v1/users/{username}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| username | string | Y | 수정할 사용자의 username (본인이어야 함) | `creator123` |

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
| avatar | string | N | 새 프로필 이미지 URL | `https://cdn.example.com/new-avatar.jpg` |
| bio | string | N | 새 자기소개 (최대 200자) | `판타지와 SF 세계관을 만드는 작가입니다.` |

**Request Example**
```json
{
  "avatar": "https://cdn.example.com/new-avatar.jpg",
  "bio": "판타지와 SF 세계관을 만드는 작가입니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 사용자 ID | `1` |
| username | string | Y | 사용자 이름 | `creator123` |
| avatar | string | N | 업데이트된 프로필 이미지 URL | `https://cdn.example.com/new-avatar.jpg` |
| bio | string | N | 업데이트된 자기소개 | `판타지와 SF 세계관을 만드는 작가입니다.` |

**Success Response Example**

200 OK
```json
{
  "id": 1,
  "username": "creator123",
  "avatar": "https://cdn.example.com/new-avatar.jpg",
  "bio": "판타지와 SF 세계관을 만드는 작가입니다."
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

403 Forbidden — 타인의 프로필 수정 시도
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "본인의 프로필만 수정할 수 있습니다."
  }
}
```
