# Pull Requests — 조회 API

Base URL: `/api/v1`

---

## GET /api/v1/pull-requests/{pr_id}

관련 페이지: `pages/11-pr-detail`

PR 상세 정보를 반환한다. PUBLIC PR은 누구나 조회 가능하며, PRIVATE PR은 작성자와 해당 Repository 원작자만 조회 가능하다. 원작자가 조회하면 ViewLog가 자동으로 기록되고 AuditLog(`PR_VIEW`)가 남는다. 단, PR 작성자 본인이 조회하는 경우에는 ViewLog를 기록하지 않는다.

**Endpoint**
```
GET /api/v1/pull-requests/{pr_id}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pr_id | integer | Y | PR ID | `42` |

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | N | Bearer access token. PRIVATE PR 조회 및 ViewLog 기록에 필요 | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/pull-requests/42
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | PR ID | `42` |
| repository | object | Y | 대상 Repository 정보 | `{...}` |
| repository.id | integer | Y | Repository ID | `1` |
| repository.title | string | Y | Repository 제목 | `내 판타지 세계관` |
| repository.author | object | Y | Repository 원작자 | `{...}` |
| repository.author.username | string | Y | 원작자 username | `creator123` |
| author | object | Y | PR 작성자 정보 | `{...}` |
| author.id | integer | Y | 작성자 ID | `2` |
| author.username | string | Y | 작성자 username | `contributor123` |
| author.avatar | string | N | 작성자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| title | string | N | PR 제목 (AI 생성). 분석 전이면 null | `마법사 아르카의 숨겨진 과거` |
| raw_content | string | N | 사용자가 자유롭게 작성한 원문 | `아이디어 내용...` |
| contribution_types | array | Y | 기여 유형 목록 | `["character_add"]` |
| visibility | string | Y | 공개 여부 (`PUBLIC`, `PRIVATE`) | `PUBLIC` |
| status | string | Y | PR 상태 | `SUBMITTED` |
| contributor_comment | string | N | 컨트리뷰터 의견 | `AI 분석에서 놓친 부분이...` |
| author_grade_override | string | N | 원작자 확정 등급 (`MAJOR`, `NORMAL`, `MINOR`). 없으면 null | `null` |
| author_grade_override_reason | string | N | 등급 조정 사유 | `null` |
| author_review_comment | string | N | 원작자 검토 코멘트 | `null` |
| changes_requested_reason | string | N | 수정 요청 사유 | `null` |
| reject_reason | object | N | 현재 거절 사유 (REJECTED 상태일 때). 없으면 null | `null` |
| reject_reason.id | integer | N | RejectReason ID | `1` |
| reject_reason.category | string | N | 거절 카테고리 | `CONFLICT` |
| reject_reason.detail | string | N | 거절 상세 사유 | `기존 세계관과 충돌합니다.` |
| reject_reason.created_at | string | N | 등록 시각 (ISO 8601 UTC) | `2024-01-02T10:00:00Z` |
| merge_info | object | N | Merge 정보 (MERGED 상태일 때). 없으면 null | `null` |
| merge_info.id | integer | N | Merge ID | `5` |
| merge_info.final_grade | string | N | 최종 등급 | `MAJOR` |
| merge_info.credit_text | string | N | 크레딧 문구 | `아르카의 숨겨진 과거 — 기여: @contributor123` |
| merge_info.author_comment | string | N | 원작자 코멘트 | `훌륭한 기여입니다.` |
| merge_info.citation_url | string | N | 퍼머링크 URL | `https://worldbuild.example.com/m/5` |
| merge_info.merged_at | string | N | 병합 시각 (ISO 8601 UTC) | `2024-01-03T12:00:00Z` |
| view_log_summary | object | N | 원작자 열람 기록 요약 (PR 작성자 본인 조회 시에만 포함) | `{...}` |
| view_log_summary.total_views | integer | N | 총 열람 횟수 | `3` |
| view_log_summary.first_viewed_at | string | N | 최초 열람 시각 (ISO 8601 UTC) | `2024-01-01T12:00:00Z` |
| first_drafted_at | string | Y | 첫 작성 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:00:00.000000Z` |
| submitted_at | string | N | 제출 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T01:00:00.000000Z` |
| reviewed_at | string | N | 가장 최근 원작자 액션 시각 | `null` |
| merged_at | string | N | 병합 시각 | `null` |
| created_at | string | Y | 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |
| updated_at | string | Y | 최근 수정 시각 (ISO 8601 UTC) | `2024-01-01T01:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 42,
  "repository": {
    "id": 1,
    "title": "내 판타지 세계관",
    "author": {
      "username": "creator123"
    }
  },
  "author": {
    "id": 2,
    "username": "contributor123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "title": "마법사 아르카의 숨겨진 과거",
  "raw_content": "아르카는 사실 마법사 가문의 후손이 아니라...",
  "contribution_types": ["character_add", "worldbuilding"],
  "visibility": "PUBLIC",
  "status": "SUBMITTED",
  "contributor_comment": "AI 분석에서 놓친 부분이 있습니다...",
  "author_grade_override": null,
  "author_grade_override_reason": null,
  "author_review_comment": null,
  "changes_requested_reason": null,
  "reject_reason": null,
  "merge_info": null,
  "view_log_summary": {
    "total_views": 2,
    "first_viewed_at": "2024-01-01T12:00:00Z"
  },
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "submitted_at": "2024-01-01T01:00:00.000000Z",
  "reviewed_at": null,
  "merged_at": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z"
}
```

**Error Response Example**

403 Forbidden — PRIVATE PR에 권한 없는 사용자 접근
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "열람 권한이 없습니다."
  }
}
```

404 Not Found
```json
{
  "error": {
    "code": "PR_NOT_FOUND",
    "message": "존재하지 않는 PR입니다."
  }
}
```

---

## GET /api/v1/pull-requests

관련 페이지: `pages/11-pr-detail`

PR 목록을 검색·필터링하여 반환한다. 비로그인 사용자는 PUBLIC PR만 조회 가능하다.

**Endpoint**
```
GET /api/v1/pull-requests
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | N | Repository ID 필터 | `1` |
| author | string | N | 작성자 username 필터 | `contributor123` |
| status | string | N | 상태 필터. 반복 가능 | `SUBMITTED` |
| type | string | N | 기여 유형 필터 | `character_add` |
| grade | string | N | AI 등급 필터 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | N | Bearer access token. 본인의 PRIVATE PR 조회 시 필요 | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/pull-requests?repo_id=1&status=SUBMITTED&grade=MAJOR&page=1&size=20
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
| items[].author | object | Y | 작성자 정보 | `{...}` |
| items[].author.username | string | Y | username | `contributor123` |
| items[].title | string | N | PR 제목 (AI 생성) | `마법사 아르카의 숨겨진 과거` |
| items[].status | string | Y | PR 상태 | `SUBMITTED` |
| items[].visibility | string | Y | 공개 여부 | `PUBLIC` |
| items[].contribution_types | array | Y | 기여 유형 목록 | `["character_add"]` |
| items[].ai_grade | string | N | AI 판정 등급 | `MAJOR` |
| items[].submitted_at | string | N | 제출 시각 (ISO 8601 UTC) | `2024-01-01T01:00:00Z` |
| total | integer | Y | 전체 결과 수 | `30` |
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
      "author": {
        "username": "contributor123",
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "title": "마법사 아르카의 숨겨진 과거",
      "status": "SUBMITTED",
      "visibility": "PUBLIC",
      "contribution_types": ["character_add", "worldbuilding"],
      "ai_grade": "MAJOR",
      "submitted_at": "2024-01-01T01:00:00Z"
    }
  ],
  "total": 30,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "서버 오류가 발생했습니다."
  }
}
```
