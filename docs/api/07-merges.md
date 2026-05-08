# Merges API

Base URL: `/api/v1/merges`

---

## GET /api/v1/merges/{merge_id}

관련 페이지: `pages/16-merge-permalink`

병합된 기여의 공개 인용 정보를 반환한다. 누구나 접근 가능하며, 이 URL이 `citation_url`로 사용된다.

**Endpoint**
```
GET /api/v1/merges/{merge_id}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| merge_id | integer | Y | Merge ID | `5` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/merges/5
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | Merge ID | `5` |
| pull_request | object | Y | 관련 PR 정보 | `{...}` |
| pull_request.id | integer | Y | PR ID | `42` |
| pull_request.title | string | Y | PR 제목 (AI 생성) | `마법사 아르카의 숨겨진 과거` |
| pull_request.summary | string | N | AI 생성 요약 | `주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안` |
| pull_request.contribution_types | array | Y | 기여 유형 목록 | `["character_add"]` |
| pull_request.first_drafted_at | string | Y | 첫 작성 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:00:00.000000Z` |
| pull_request.submitted_at | string | Y | 제출 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T01:00:00.000000Z` |
| repository | object | Y | 대상 Repository 정보 | `{...}` |
| repository.id | integer | Y | Repository ID | `1` |
| repository.title | string | Y | Repository 제목 | `내 판타지 세계관` |
| repository.thumbnail | string | N | Repository 썸네일 URL | `https://cdn.example.com/thumb.jpg` |
| contributor | object | Y | 기여자 정보 | `{...}` |
| contributor.username | string | Y | 기여자 username | `contributor123` |
| contributor.avatar | string | N | 기여자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| author | object | Y | 원작자 정보 | `{...}` |
| author.username | string | Y | 원작자 username | `creator123` |
| author.avatar | string | N | 원작자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| final_grade | string | Y | 최종 등급 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| credit_text | string | Y | 크레딧 문구 | `아르카의 숨겨진 과거 — 기여: @contributor123` |
| author_comment | string | N | 원작자 코멘트 | `훌륭한 기여입니다.` |
| citation_url | string | Y | 퍼머링크 URL | `https://worldbuild.example.com/m/5` |
| merged_at | string | Y | 병합 시각 (ISO 8601 UTC, microseconds) | `2024-01-03T12:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "id": 5,
  "pull_request": {
    "id": 42,
    "title": "마법사 아르카의 숨겨진 과거",
    "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
    "contribution_types": ["character_add", "worldbuilding"],
    "first_drafted_at": "2024-01-01T00:00:00.000000Z",
    "submitted_at": "2024-01-01T01:00:00.000000Z"
  },
  "repository": {
    "id": 1,
    "title": "내 판타지 세계관",
    "thumbnail": "https://cdn.example.com/thumb.jpg"
  },
  "contributor": {
    "username": "contributor123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "author": {
    "username": "creator123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "final_grade": "MAJOR",
  "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor123",
  "author_comment": "훌륭한 기여입니다. 공식 설정으로 반영합니다.",
  "citation_url": "https://worldbuild.example.com/m/5",
  "merged_at": "2024-01-03T12:00:00.000000Z"
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "MERGE_NOT_FOUND",
    "message": "존재하지 않는 기여 기록입니다."
  }
}
```
