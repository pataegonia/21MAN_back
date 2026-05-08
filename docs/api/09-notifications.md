# Notifications API

Base URL: `/api/v1/notifications`

---

## GET /api/v1/notifications

관련 페이지: `pages/15-notifications`

현재 로그인한 사용자의 알림 목록을 반환한다. 생성일 내림차순으로 정렬된다.

**Endpoint**
```
GET /api/v1/notifications
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| unread_only | boolean | N | true이면 읽지 않은 알림만 반환. 기본값: `false` | `true` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/notifications?unread_only=true&page=1&size=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | 알림 목록 | `[...]` |
| items[].id | integer | Y | 알림 ID | `10` |
| items[].type | string | Y | 알림 유형 (`PR_SUBMITTED`, `PR_RESUBMITTED`, `PR_COMMENT_ADDED`, `PR_ACCEPTED`, `PR_CHANGES_REQUESTED`, `PR_REJECTED`, `PR_MERGED`, `GRADE_ADJUSTED`) | `PR_MERGED` |
| items[].payload | object | Y | 알림 상세 데이터 | `{...}` |
| items[].payload.pr_id | integer | N | 관련 PR ID | `42` |
| items[].payload.pr_title | string | N | 관련 PR 제목 | `마법사 아르카의 숨겨진 과거` |
| items[].payload.repo_id | integer | N | 관련 Repository ID | `1` |
| items[].payload.repo_title | string | N | 관련 Repository 제목 | `내 판타지 세계관` |
| items[].payload.actor_id | integer | N | 액션을 수행한 사용자 ID | `1` |
| items[].payload.actor_username | string | N | 액션을 수행한 사용자 username | `creator123` |
| items[].is_read | boolean | Y | 읽음 여부 | `false` |
| items[].created_at | string | Y | 알림 생성 시각 (ISO 8601 UTC) | `2024-01-03T12:00:00Z` |
| items[].read_at | string | N | 읽음 처리 시각 (ISO 8601 UTC). 미읽음이면 null | `null` |
| total | integer | Y | 전체 결과 수 | `15` |
| unread_count | integer | Y | 읽지 않은 알림 수 | `3` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "id": 10,
      "type": "PR_MERGED",
      "payload": {
        "pr_id": 42,
        "pr_title": "마법사 아르카의 숨겨진 과거",
        "repo_id": 1,
        "repo_title": "내 판타지 세계관",
        "actor_id": 1,
        "actor_username": "creator123"
      },
      "is_read": false,
      "created_at": "2024-01-03T12:00:00Z",
      "read_at": null
    }
  ],
  "total": 15,
  "unread_count": 3,
  "page": 1,
  "size": 20
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

---

## GET /api/v1/notifications/unread-count

관련 페이지: `pages/15-notifications`

읽지 않은 알림 수를 반환한다. 헤더 뱃지 카운터용 경량 엔드포인트다.

**Endpoint**
```
GET /api/v1/notifications/unread-count
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
GET /api/v1/notifications/unread-count
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| count | integer | Y | 읽지 않은 알림 수 | `3` |

**Success Response Example**

200 OK
```json
{
  "count": 3
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

---

## POST /api/v1/notifications/{id}/read

관련 페이지: `pages/15-notifications`

특정 알림을 읽음 처리한다.

**Endpoint**
```
POST /api/v1/notifications/{id}/read
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 알림 ID | `10` |

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
POST /api/v1/notifications/10/read
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | 알림 ID | `10` |
| is_read | boolean | Y | 읽음 여부 | `true` |
| read_at | string | Y | 읽음 처리 시각 (ISO 8601 UTC) | `2024-01-04T09:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 10,
  "is_read": true,
  "read_at": "2024-01-04T09:00:00Z"
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

403 Forbidden — 타인의 알림 읽음 처리 시도
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "본인의 알림만 읽음 처리할 수 있습니다."
  }
}
```

404 Not Found
```json
{
  "error": {
    "code": "NOTIFICATION_NOT_FOUND",
    "message": "존재하지 않는 알림입니다."
  }
}
```

---

## POST /api/v1/notifications/read-all

관련 페이지: `pages/15-notifications`

현재 로그인한 사용자의 모든 읽지 않은 알림을 일괄 읽음 처리한다.

**Endpoint**
```
POST /api/v1/notifications/read-all
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
POST /api/v1/notifications/read-all
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| updated_count | integer | Y | 읽음 처리된 알림 수 | `3` |

**Success Response Example**

200 OK
```json
{
  "updated_count": 3
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
