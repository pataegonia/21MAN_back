# Repositories API

Base URL: `/api/v1/repositories`

---

## POST /api/v1/repositories

관련 페이지: `pages/06-repository-create`

Repository를 생성한다. 요청한 사용자가 자동으로 원작자(author)로 등록된다.

**Endpoint**
```
POST /api/v1/repositories
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
| title | string | Y | 작품 제목 (최대 100자) | `내 판타지 세계관` |
| description | string | N | 작품 설명 (최대 500자) | `마법이 존재하는 세계의 이야기` |
| thumbnail | string | N | 썸네일 이미지 URL | `https://cdn.example.com/thumb.jpg` |
| tags | array | N | 태그 목록 (최대 10개) | `["판타지", "마법"]` |
| external_links | array | N | 외부 링크 목록 (최대 3개) | `["https://example.com"]` |
| readme | object | N | README 구조화 정보 | `{...}` |
| readme.content | string | N | 작품 설명 (마크다운) | `## 세계관 소개\n...` |
| readme.characters | array | N | 주요 캐릭터 목록 | `[{"name": "아르카", "description": "주인공"}]` |
| readme.characters[].name | string | Y | 캐릭터 이름 | `아르카` |
| readme.characters[].description | string | N | 캐릭터 설명 | `주인공 마법사` |
| readme.regions | array | N | 주요 지역 목록 | `[{"name": "에테르 왕국", "description": "마법 왕국"}]` |
| readme.regions[].name | string | Y | 지역 이름 | `에테르 왕국` |
| readme.regions[].description | string | N | 지역 설명 | `마법이 가장 발달한 나라` |
| readme.world_rules | array | N | 핵심 세계관 규칙 목록 | `["마법은 감정에 반응한다"]` |
| readme.forbidden_settings | array | N | 금지 설정 목록 | `["신이 직접 등장하는 설정"]` |
| recruiting_areas | array | N | 모집 중인 기여 영역 | `["character_add", "worldbuilding"]` |
| contribution_guidelines | string | N | 기여 가이드라인 (마크다운) | `## 기여 가이드\n...` |

**Request Example**
```json
{
  "title": "내 판타지 세계관",
  "description": "마법이 존재하는 세계의 이야기",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "tags": ["판타지", "마법"],
  "external_links": ["https://example.com"],
  "readme": {
    "content": "## 세계관 소개\n이 세계에는 마법이 존재합니다.",
    "characters": [
      { "name": "아르카", "description": "주인공 마법사" }
    ],
    "regions": [
      { "name": "에테르 왕국", "description": "마법이 가장 발달한 나라" }
    ],
    "world_rules": ["마법은 감정에 반응한다"],
    "forbidden_settings": ["신이 직접 등장하는 설정"]
  },
  "recruiting_areas": ["character_add", "worldbuilding"],
  "contribution_guidelines": "## 기여 가이드\n세계관을 존중해주세요."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | Repository ID | `1` |
| title | string | Y | 작품 제목 | `내 판타지 세계관` |
| author | object | Y | 원작자 정보 | `{...}` |
| author.id | integer | Y | 원작자 ID | `1` |
| author.username | string | Y | 원작자 username | `creator123` |
| created_at | string | Y | 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |

**Success Response Example**

201 Created
```json
{
  "id": 1,
  "title": "내 판타지 세계관",
  "description": "마법이 존재하는 세계의 이야기",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "tags": ["판타지", "마법"],
  "author": {
    "id": 1,
    "username": "creator123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "recruiting_areas": ["character_add", "worldbuilding"],
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

422 Unprocessable Entity
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 유효하지 않습니다.",
    "details": [
      { "field": "title", "message": "제목은 필수입니다." }
    ]
  }
}
```

---

## GET /api/v1/repositories

관련 페이지: `pages/04-repository-list`, `pages/02-home`

Repository 목록을 조회한다. 키워드, 태그, 모집 영역, 정렬 기준으로 필터링할 수 있다.

**Endpoint**
```
GET /api/v1/repositories
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| q | string | N | 키워드 검색 (제목·설명·원작자 username) | `판타지` |
| tag | string | N | 태그 필터. 반복 가능 (AND 조건) | `판타지` |
| recruiting | string | N | 모집 영역 필터 | `character_add` |
| sort | string | N | 정렬 기준 (`latest`, `popular`). 기본값: `latest` | `popular` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/repositories?q=판타지&tag=마법&sort=popular&page=1&size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | Repository 목록 | `[...]` |
| items[].id | integer | Y | Repository ID | `1` |
| items[].title | string | Y | 작품 제목 | `내 판타지 세계관` |
| items[].description | string | N | 작품 설명 | `마법이 존재하는 세계의 이야기` |
| items[].thumbnail | string | N | 썸네일 URL | `https://cdn.example.com/thumb.jpg` |
| items[].tags | array | Y | 태그 목록 | `["판타지", "마법"]` |
| items[].author | object | Y | 원작자 정보 | `{...}` |
| items[].author.username | string | Y | 원작자 username | `creator123` |
| items[].author.avatar | string | N | 원작자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| items[].merge_count | integer | Y | Merge된 기여 수 | `5` |
| items[].pr_count | integer | Y | 전체 PR 수 | `12` |
| items[].recruiting_areas | array | Y | 모집 중인 기여 영역 | `["character_add"]` |
| items[].created_at | string | Y | 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |
| items[].updated_at | string | Y | 최근 수정 시각 (ISO 8601 UTC) | `2024-06-01T00:00:00Z` |
| total | integer | Y | 전체 결과 수 | `200` |
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
      "description": "마법이 존재하는 세계의 이야기",
      "thumbnail": "https://cdn.example.com/thumb.jpg",
      "tags": ["판타지", "마법"],
      "author": {
        "username": "creator123",
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "merge_count": 5,
      "pr_count": 12,
      "recruiting_areas": ["character_add", "worldbuilding"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-06-01T00:00:00Z"
    }
  ],
  "total": 200,
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

---

## GET /api/v1/repositories/{repo_id}

관련 페이지: `pages/05-repository-detail`

Repository 상세 정보를 반환한다. README 자식 컬렉션(캐릭터, 지역, 규칙 등)이 포함된다.

**Endpoint**
```
GET /api/v1/repositories/{repo_id}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/repositories/1
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | Repository ID | `1` |
| title | string | Y | 작품 제목 | `내 판타지 세계관` |
| description | string | N | 작품 설명 | `마법이 존재하는 세계의 이야기` |
| thumbnail | string | N | 썸네일 URL | `https://cdn.example.com/thumb.jpg` |
| tags | array | Y | 태그 목록 | `["판타지", "마법"]` |
| external_links | array | Y | 외부 링크 목록 | `["https://example.com"]` |
| author | object | Y | 원작자 정보 | `{...}` |
| author.id | integer | Y | 원작자 ID | `1` |
| author.username | string | Y | 원작자 username | `creator123` |
| author.avatar | string | N | 원작자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| readme | object | Y | README 구조화 정보 | `{...}` |
| readme.content | string | N | 작품 설명 (마크다운) | `## 세계관 소개\n...` |
| readme.characters | array | Y | 주요 캐릭터 목록 | `[...]` |
| readme.regions | array | Y | 주요 지역 목록 | `[...]` |
| readme.world_rules | array | Y | 핵심 세계관 규칙 목록 | `[...]` |
| readme.forbidden_settings | array | Y | 금지 설정 목록 | `[...]` |
| recruiting_areas | array | Y | 모집 중인 기여 영역 | `["character_add"]` |
| contribution_guidelines | string | N | 기여 가이드라인 (마크다운) | `## 기여 가이드\n...` |
| merge_count | integer | Y | Merge된 기여 수 | `5` |
| pr_count | integer | Y | 전체 PR 수 | `12` |
| created_at | string | Y | 생성 시각 (ISO 8601 UTC) | `2024-01-01T00:00:00Z` |
| updated_at | string | Y | 최근 수정 시각 (ISO 8601 UTC) | `2024-06-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 1,
  "title": "내 판타지 세계관",
  "description": "마법이 존재하는 세계의 이야기",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "tags": ["판타지", "마법"],
  "external_links": ["https://example.com"],
  "author": {
    "id": 1,
    "username": "creator123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "readme": {
    "content": "## 세계관 소개\n이 세계에는 마법이 존재합니다.",
    "characters": [
      { "name": "아르카", "description": "주인공 마법사" }
    ],
    "regions": [
      { "name": "에테르 왕국", "description": "마법이 가장 발달한 나라" }
    ],
    "world_rules": ["마법은 감정에 반응한다"],
    "forbidden_settings": ["신이 직접 등장하는 설정"]
  },
  "recruiting_areas": ["character_add", "worldbuilding"],
  "contribution_guidelines": "## 기여 가이드\n세계관을 존중해주세요.",
  "merge_count": 5,
  "pr_count": 12,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-06-01T00:00:00Z"
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```

---

## PATCH /api/v1/repositories/{repo_id}

관련 페이지: `pages/07-repository-edit`

Repository 정보를 수정한다. 자식 컬렉션(characters, regions, world_rules, forbidden_settings, recruiting_areas)은 전체 배열 교체 방식으로 저장된다. 수정 후 AuditLog(`REPO_UPDATE`)가 기록된다.

**Endpoint**
```
PATCH /api/v1/repositories/{repo_id}
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| title | string | N | 작품 제목 (최대 100자) | `수정된 판타지 세계관` |
| description | string | N | 작품 설명 (최대 500자) | `수정된 설명` |
| thumbnail | string | N | 썸네일 이미지 URL | `https://cdn.example.com/new-thumb.jpg` |
| tags | array | N | 태그 목록 전체 교체 (최대 10개) | `["판타지"]` |
| external_links | array | N | 외부 링크 목록 전체 교체 (최대 3개) | `["https://example.com"]` |
| readme | object | N | README 구조화 정보 전체 교체 | `{...}` |
| readme.content | string | N | 작품 설명 (마크다운) | `## 수정된 세계관 소개\n...` |
| readme.characters | array | N | 주요 캐릭터 목록 전체 교체 | `[...]` |
| readme.regions | array | N | 주요 지역 목록 전체 교체 | `[...]` |
| readme.world_rules | array | N | 핵심 세계관 규칙 목록 전체 교체 | `[...]` |
| readme.forbidden_settings | array | N | 금지 설정 목록 전체 교체 | `[...]` |
| recruiting_areas | array | N | 모집 영역 목록 전체 교체 | `["character_add"]` |
| contribution_guidelines | string | N | 기여 가이드라인 (마크다운) | `## 수정된 가이드\n...` |

**Request Example**
```json
{
  "title": "수정된 판타지 세계관",
  "tags": ["판타지"],
  "readme": {
    "content": "## 수정된 세계관 소개\n이 세계에는 마법이 존재합니다.",
    "characters": [
      { "name": "아르카", "description": "수정된 설명" }
    ],
    "regions": [],
    "world_rules": ["마법은 감정에 반응한다", "마법 사용 시 체력이 소모된다"],
    "forbidden_settings": ["신이 직접 등장하는 설정"]
  },
  "recruiting_areas": ["character_add"]
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | Repository ID | `1` |
| title | string | Y | 수정된 작품 제목 | `수정된 판타지 세계관` |
| updated_at | string | Y | 수정 시각 (ISO 8601 UTC) | `2024-06-01T00:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "id": 1,
  "title": "수정된 판타지 세계관",
  "description": "마법이 존재하는 세계의 이야기",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "tags": ["판타지"],
  "external_links": ["https://example.com"],
  "author": {
    "id": 1,
    "username": "creator123",
    "avatar": "https://cdn.example.com/avatar.jpg"
  },
  "readme": {
    "content": "## 수정된 세계관 소개\n이 세계에는 마법이 존재합니다.",
    "characters": [
      { "name": "아르카", "description": "수정된 설명" }
    ],
    "regions": [],
    "world_rules": ["마법은 감정에 반응한다", "마법 사용 시 체력이 소모된다"],
    "forbidden_settings": ["신이 직접 등장하는 설정"]
  },
  "recruiting_areas": ["character_add"],
  "contribution_guidelines": "## 기여 가이드\n세계관을 존중해주세요.",
  "updated_at": "2024-06-01T00:00:00Z"
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

403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "원작자만 Repository를 수정할 수 있습니다."
  }
}
```

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```

---

## GET /api/v1/repositories/{repo_id}/contributors

관련 페이지: `pages/05-repository-detail`

Repository에 Merge된 기여자 집계 목록을 반환한다.

**Endpoint**
```
GET /api/v1/repositories/{repo_id}/contributors
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/repositories/1/contributors
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| contributors | array | Y | 기여자 목록 (Merge 수 내림차순) | `[...]` |
| contributors[].user | object | Y | 사용자 정보 | `{...}` |
| contributors[].user.username | string | Y | username | `contributor123` |
| contributors[].user.avatar | string | N | 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| contributors[].major_count | integer | Y | MAJOR Merge 수 | `2` |
| contributors[].normal_count | integer | Y | NORMAL Merge 수 | `3` |
| contributors[].minor_count | integer | Y | MINOR Merge 수 | `1` |
| contributors[].total_count | integer | Y | 전체 Merge 수 | `6` |

**Success Response Example**

200 OK
```json
{
  "contributors": [
    {
      "user": {
        "username": "contributor123",
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "major_count": 2,
      "normal_count": 3,
      "minor_count": 1,
      "total_count": 6
    }
  ]
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```

---

## GET /api/v1/repositories/{repo_id}/merges

관련 페이지: `pages/05-repository-detail`

Repository에 Merge된 기여 이력을 반환한다.

**Endpoint**
```
GET /api/v1/repositories/{repo_id}/merges
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

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
GET /api/v1/repositories/1/merges?page=1&size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | Merge 이력 목록 (병합일 내림차순) | `[...]` |
| items[].id | integer | Y | Merge ID | `5` |
| items[].pull_request | object | Y | 관련 PR 정보 | `{...}` |
| items[].pull_request.id | integer | Y | PR ID | `42` |
| items[].pull_request.title | string | Y | PR 제목 | `마법사 아르카의 숨겨진 과거` |
| items[].contributor | object | Y | 기여자 정보 | `{...}` |
| items[].contributor.username | string | Y | username | `contributor123` |
| items[].contributor.avatar | string | N | 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| items[].final_grade | string | Y | 최종 등급 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| items[].credit_text | string | Y | 크레딧 문구 | `아르카의 숨겨진 과거 — 기여: @contributor123` |
| items[].merged_at | string | Y | 병합 시각 (ISO 8601 UTC) | `2024-01-03T12:00:00Z` |
| total | integer | Y | 전체 결과 수 | `5` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "id": 5,
      "pull_request": {
        "id": 42,
        "title": "마법사 아르카의 숨겨진 과거"
      },
      "contributor": {
        "username": "contributor123",
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "final_grade": "MAJOR",
      "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor123",
      "merged_at": "2024-01-03T12:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```

---

## GET /api/v1/repositories/{repo_id}/pull-requests

관련 페이지: `pages/05-repository-detail`, `pages/11-pr-detail`

Repository에 제출된 PR 목록을 반환한다. 원작자는 전체 조회, 그 외는 PUBLIC PR만 조회 가능하다.

**Endpoint**
```
GET /api/v1/repositories/{repo_id}/pull-requests
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| status | string | N | 상태 필터. 반복 가능 | `SUBMITTED` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | N | Bearer access token. 원작자 전체 조회 시 필요 | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/repositories/1/pull-requests?status=SUBMITTED&page=1&size=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| items | array | Y | PR 목록 | `[...]` |
| items[].id | integer | Y | PR ID | `42` |
| items[].author | object | Y | 작성자 정보 | `{...}` |
| items[].author.username | string | Y | username | `contributor123` |
| items[].author.avatar | string | N | 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| items[].title | string | N | PR 제목 (AI 생성) | `마법사 아르카의 숨겨진 과거` |
| items[].status | string | Y | PR 상태 | `SUBMITTED` |
| items[].visibility | string | Y | 공개 여부 (`PUBLIC`, `PRIVATE`) | `PUBLIC` |
| items[].contribution_types | array | Y | 기여 유형 목록 | `["character_add"]` |
| items[].ai_grade | string | N | AI 판정 등급 | `MAJOR` |
| items[].author_grade_override | string | N | 원작자 확정 등급 | `null` |
| items[].submitted_at | string | N | 제출 시각 (ISO 8601 UTC) | `2024-01-01T01:00:00Z` |
| total | integer | Y | 전체 결과 수 | `12` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "items": [
    {
      "id": 42,
      "author": {
        "username": "contributor123",
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "title": "마법사 아르카의 숨겨진 과거",
      "status": "SUBMITTED",
      "visibility": "PUBLIC",
      "contribution_types": ["character_add"],
      "ai_grade": "MAJOR",
      "author_grade_override": null,
      "submitted_at": "2024-01-01T01:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "size": 20
}
```

**Error Response Example**

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```

---

## GET /api/v1/repositories/{repo_id}/stats

관련 페이지: `pages/05-repository-detail`

Repository의 통계 정보를 반환한다. 원작자만 조회 가능하다.

**Endpoint**
```
GET /api/v1/repositories/{repo_id}/stats
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | Repository ID | `1` |

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/repositories/1/stats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| received_prs | integer | Y | 받은 전체 PR 수 (DRAFT 제외) | `25` |
| merged_prs | integer | Y | Merge한 PR 수 | `12` |
| merge_ratio | number | Y | Merge 비율 (0.00~1.00) | `0.48` |
| avg_review_days | number | Y | 평균 검토 기간 (일 단위) | `2.5` |
| rejected_prs | integer | Y | 거절한 PR 수 | `5` |
| pending_prs | integer | Y | 검토 대기 중인 PR 수 (SUBMITTED + ACCEPTED) | `8` |

**Success Response Example**

200 OK
```json
{
  "received_prs": 25,
  "merged_prs": 12,
  "merge_ratio": 0.48,
  "avg_review_days": 2.5,
  "rejected_prs": 5,
  "pending_prs": 8
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

403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "원작자만 통계를 조회할 수 있습니다."
  }
}
```

404 Not Found
```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "존재하지 않는 Repository입니다."
  }
}
```
