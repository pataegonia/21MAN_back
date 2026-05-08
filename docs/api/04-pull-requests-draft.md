# Pull Requests — Draft & 작성 API

Base URL: `/api/v1`

---

## POST /api/v1/repositories/{repo_id}/pull-requests/draft

관련 페이지: `pages/08-pr-draft`

PR Draft를 생성한다. 최초 호출 시 `first_drafted_at`이 서버 시간으로 기록되며 이후 변경되지 않는다. 같은 Repository에 동일 사용자의 DRAFT가 이미 존재하면 기존 PR의 id를 반환한다.

**Endpoint**
```
POST /api/v1/repositories/{repo_id}/pull-requests/draft
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repo_id | integer | Y | 대상 Repository ID | `1` |

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
POST /api/v1/repositories/1/pull-requests/draft
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| first_drafted_at | string | Y | 첫 작성 시각. 서버 시간 기준 (ISO 8601 UTC, microseconds) | `2024-01-01T00:00:00.000000Z` |
| last_saved_at | string | Y | 마지막 저장 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:00:00.000000Z` |
| save_count | integer | Y | 저장 횟수 | `0` |
| raw_content | string | N | 작성된 원문 (신규 생성 시 null) | `null` |

**Success Response Example**

201 Created — 신규 Draft 생성
```json
{
  "pull_request_id": 42,
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "last_saved_at": "2024-01-01T00:00:00.000000Z",
  "save_count": 0,
  "raw_content": null
}
```

200 OK — 기존 Draft 반환
```json
{
  "pull_request_id": 42,
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "last_saved_at": "2024-01-01T00:15:00.000000Z",
  "save_count": 5,
  "raw_content": "작성 중인 내용..."
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

## GET /api/v1/pull-requests/{pr_id}/draft

관련 페이지: `pages/08-pr-draft`

본인의 PR Draft를 조회한다.

**Endpoint**
```
GET /api/v1/pull-requests/{pr_id}/draft
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
| Authorization | string | Y | Bearer access token (PR 작성자 본인만 가능) | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/pull-requests/42/draft
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| repository | object | Y | 대상 Repository 정보 | `{...}` |
| repository.id | integer | Y | Repository ID | `1` |
| repository.title | string | Y | Repository 제목 | `내 판타지 세계관` |
| first_drafted_at | string | Y | 첫 작성 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:00:00.000000Z` |
| last_saved_at | string | Y | 마지막 저장 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:05:00.000000Z` |
| save_count | integer | Y | 저장 횟수 | `10` |
| raw_content | string | N | 작성된 원문 | `아이디어 내용...` |
| latest_ai_analysis | object | N | 가장 최근 AI 분석 결과 요약 (없으면 null) | `null` |
| latest_ai_analysis.ai_grade | string | N | AI 판정 등급 | `MAJOR` |
| latest_ai_analysis.score_total | integer | N | 총점 | `37` |
| latest_ai_analysis.run_seq | integer | N | 분석 회차 | `1` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "repository": {
    "id": 1,
    "title": "내 판타지 세계관"
  },
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "last_saved_at": "2024-01-01T00:05:00.000000Z",
  "save_count": 10,
  "raw_content": "아이디어 내용...",
  "latest_ai_analysis": null
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
    "message": "본인의 Draft만 조회할 수 있습니다."
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

## PATCH /api/v1/pull-requests/{pr_id}/draft

관련 페이지: `pages/08-pr-draft`

PR Draft를 자동 저장한다. `raw_content`, `last_saved_at`, `save_count`만 갱신한다. `first_drafted_at`은 절대 변경하지 않는다.

**Endpoint**
```
PATCH /api/v1/pull-requests/{pr_id}/draft
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
| Authorization | string | Y | Bearer access token (PR 작성자 본인만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| raw_content | string | Y | 저장할 원문 | `작성 중인 내용...` |

**Request Example**
```json
{
  "raw_content": "아르카는 사실 마법사 가문의 후손이 아니라..."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| last_saved_at | string | Y | 갱신된 저장 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:05:30.000000Z` |
| save_count | integer | Y | 갱신된 저장 횟수 | `11` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "last_saved_at": "2024-01-01T00:05:30.000000Z",
  "save_count": 11
}
```

**Error Response Example**

400 Bad Request — DRAFT 상태가 아닌 PR에 저장 시도
```json
{
  "error": {
    "code": "PR_NOT_DRAFT",
    "message": "DRAFT 상태의 PR만 저장할 수 있습니다."
  }
}
```

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
    "message": "본인의 Draft만 수정할 수 있습니다."
  }
}
```

---

## POST /api/v1/pull-requests/{pr_id}/ai-analyze

관련 페이지: `pages/09-pr-ai-analysis`

PR 내용을 AI로 분석한다. 호출 시마다 새 AiAnalysis 행이 생성되며 `run_seq`가 증가한다. 이전 분석 결과는 보존된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/ai-analyze
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
| Authorization | string | Y | Bearer access token (PR 작성자 본인만 가능) | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
POST /api/v1/pull-requests/42/ai-analyze
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| id | integer | Y | AiAnalysis ID | `10` |
| pull_request_id | integer | Y | PR ID | `42` |
| run_seq | integer | Y | 분석 회차 (1부터 시작) | `1` |
| generated_title | string | Y | AI 생성 PR 제목 | `마법사 아르카의 숨겨진 과거 설정` |
| summary | string | Y | 내용 요약 | `주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안` |
| structured_content | object | Y | 구조화된 내용 | `{...}` |
| contribution_types | array | Y | 기여 유형 목록 | `["character_add"]` |
| score_scope | integer | Y | Scope 점수 (0~10) | `8` |
| score_permanence | integer | Y | Permanence 점수 (0~10) | `7` |
| score_cascade | integer | Y | Cascade 점수 (0~10) | `9` |
| score_alignment | integer | Y | Alignment 점수 (0~10) | `6` |
| score_specificity | integer | Y | Specificity 점수 (0~10) | `7` |
| score_total | integer | Y | 총점 (0~50) | `37` |
| ai_grade | string | Y | AI 판정 등급 (`MAJOR`, `NORMAL`, `MINOR`) | `MAJOR` |
| rationale | string | Y | 분석 근거 | `캐릭터의 출생 비밀은 세계관 전체에 영향을 미치며...` |
| missing_info | array | Y | 누락 정보 목록 | `["캐릭터의 구체적인 나이가 명시되지 않음"]` |
| conflict_checks | array | Y | 충돌 검사 결과 목록 | `[...]` |
| conflict_checks[].risk_level | string | Y | 위험도 (`LOW`, `MEDIUM`, `HIGH`) | `LOW` |
| conflict_checks[].check_target | string | Y | 검사 대상 | `readme` |
| conflict_checks[].passed | boolean | Y | 통과 여부 | `true` |
| conflict_checks[].detail | string | Y | 상세 설명 | `기존 README와 충돌 없음` |
| model_name | string | Y | 사용된 AI 모델명 | `gpt-4o-2024-08-06` |
| created_at | string | Y | 분석 생성 시각 (ISO 8601 UTC, microseconds) | `2024-01-01T00:10:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "id": 10,
  "pull_request_id": 42,
  "run_seq": 1,
  "generated_title": "마법사 아르카의 숨겨진 과거 설정",
  "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
  "structured_content": {
    "character_name": "아르카",
    "background": "귀족 가문의 사생아로 태어났으나 진실은..."
  },
  "contribution_types": ["character_add", "worldbuilding"],
  "score_scope": 8,
  "score_permanence": 7,
  "score_cascade": 9,
  "score_alignment": 6,
  "score_specificity": 7,
  "score_total": 37,
  "ai_grade": "MAJOR",
  "rationale": "캐릭터의 출생 비밀은 세계관 전체에 영향을 미치며 기존 규칙과 조화를 이룹니다.",
  "missing_info": ["캐릭터의 구체적인 나이가 명시되지 않음"],
  "conflict_checks": [
    {
      "risk_level": "LOW",
      "check_target": "readme",
      "passed": true,
      "detail": "기존 README와 충돌 없음"
    },
    {
      "risk_level": "LOW",
      "check_target": "forbidden_settings",
      "passed": true,
      "detail": "금지 설정에 해당하지 않음"
    }
  ],
  "model_name": "gpt-4o-2024-08-06",
  "created_at": "2024-01-01T00:10:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — raw_content 없음
```json
{
  "error": {
    "code": "CONTENT_REQUIRED",
    "message": "분석할 내용이 없습니다. 먼저 내용을 작성해주세요."
  }
}
```

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
    "message": "본인의 PR만 분석 요청할 수 있습니다."
  }
}
```

502 Bad Gateway — AI 서비스 오류
```json
{
  "error": {
    "code": "AI_SERVICE_ERROR",
    "message": "AI 분석에 실패했습니다. 잠시 후 다시 시도해주세요."
  }
}
```

---

## GET /api/v1/pull-requests/{pr_id}/ai-analysis

관련 페이지: `pages/09-pr-ai-analysis`, `pages/11-pr-detail`

PR의 AI 분석 결과를 반환한다. 기본값으로 가장 최근 분석 결과를 반환하며, `run_seq`로 특정 회차 조회도 가능하다.

**Endpoint**
```
GET /api/v1/pull-requests/{pr_id}/ai-analysis
```

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pr_id | integer | Y | PR ID | `42` |

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| run_seq | integer | N | 분석 회차. 지정하지 않으면 가장 최근 회차 반환 | `1` |

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| Authorization | string | Y | Bearer access token (PR 작성자 또는 원작자만 가능) | `Bearer eyJhbGci...` |

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/pull-requests/42/ai-analysis
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Body**

`POST /api/v1/pull-requests/{pr_id}/ai-analyze`의 Response Body와 동일한 구조.

**Success Response Example**

200 OK
```json
{
  "id": 10,
  "pull_request_id": 42,
  "run_seq": 1,
  "generated_title": "마법사 아르카의 숨겨진 과거 설정",
  "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
  "structured_content": { "character_name": "아르카" },
  "contribution_types": ["character_add", "worldbuilding"],
  "score_scope": 8,
  "score_permanence": 7,
  "score_cascade": 9,
  "score_alignment": 6,
  "score_specificity": 7,
  "score_total": 37,
  "ai_grade": "MAJOR",
  "rationale": "캐릭터의 출생 비밀은 세계관 전체에 영향을 미치며 기존 규칙과 조화를 이룹니다.",
  "missing_info": ["캐릭터의 구체적인 나이가 명시되지 않음"],
  "conflict_checks": [
    {
      "risk_level": "LOW",
      "check_target": "readme",
      "passed": true,
      "detail": "기존 README와 충돌 없음"
    }
  ],
  "model_name": "gpt-4o-2024-08-06",
  "created_at": "2024-01-01T00:10:00.000000Z"
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
    "message": "PR 작성자 또는 원작자만 AI 분석 결과를 조회할 수 있습니다."
  }
}
```

404 Not Found — 분석 결과 없음
```json
{
  "error": {
    "code": "ANALYSIS_NOT_FOUND",
    "message": "AI 분석 결과가 없습니다."
  }
}
```

---

## POST /api/v1/pull-requests/{pr_id}/submit

관련 페이지: `pages/10-pr-submit`

PR을 최종 제출한다. 상태가 DRAFT → SUBMITTED로 변경되며, `submitted_at`이 서버 시간으로 기록된다. 제출 후 원작자에게 알림이 생성되고 AuditLog(`PR_SUBMIT`)가 기록된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/submit
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
| Authorization | string | Y | Bearer access token (PR 작성자 본인만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| visibility | string | Y | 공개 여부 (`PUBLIC`, `PRIVATE`) | `PUBLIC` |

**Request Example**
```json
{
  "visibility": "PUBLIC"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| status | string | Y | 변경된 상태 | `SUBMITTED` |
| visibility | string | Y | 공개 여부 | `PUBLIC` |
| submitted_at | string | Y | 제출 시각. 서버 시간 기준 (ISO 8601 UTC, microseconds) | `2024-01-01T01:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "status": "SUBMITTED",
  "visibility": "PUBLIC",
  "submitted_at": "2024-01-01T01:00:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — DRAFT 상태가 아닌 PR 제출 시도
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "DRAFT 상태의 PR만 제출할 수 있습니다."
  }
}
```

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
    "message": "본인의 PR만 제출할 수 있습니다."
  }
}
```

---

## PATCH /api/v1/pull-requests/{pr_id}/contributor-comment

관련 페이지: `pages/09-pr-ai-analysis`, `pages/10-pr-submit`

PR에 대한 컨트리뷰터 의견을 작성하거나 수정한다.

**Endpoint**
```
PATCH /api/v1/pull-requests/{pr_id}/contributor-comment
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
| Authorization | string | Y | Bearer access token (PR 작성자 본인만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| contributor_comment | string | Y | 컨트리뷰터 의견 (AI 분석에 대한 동의/이의/추가 설명) | `AI 분석에서 놓친 부분이 있습니다...` |

**Request Example**
```json
{
  "contributor_comment": "AI 분석에서 놓친 부분이 있습니다. 이 캐릭터의 능력은 기존 마법 체계와 다르게 설계되었으므로 충돌이 없습니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| contributor_comment | string | Y | 저장된 컨트리뷰터 의견 | `AI 분석에서 놓친 부분이 있습니다...` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "contributor_comment": "AI 분석에서 놓친 부분이 있습니다. 이 캐릭터의 능력은 기존 마법 체계와 다르게 설계되었으므로 충돌이 없습니다."
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
    "message": "본인의 PR에만 의견을 작성할 수 있습니다."
  }
}
```
