# Pull Requests — 원작자 액션 API

Base URL: `/api/v1`

모든 엔드포인트는 해당 Repository의 원작자만 호출 가능하다. 모든 액션은 AuditLog에 기록된다.

---

## POST /api/v1/pull-requests/{pr_id}/accept

관련 페이지: `pages/12-pr-review`

PR을 수락한다. 상태가 SUBMITTED → ACCEPTED로 변경되며, 컨트리뷰터에게 `PR_ACCEPTED` 알림이 전송된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/accept
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| comment | string | N | 원작자 검토 코멘트 | `흥미로운 캐릭터 설정입니다.` |

**Request Example**
```json
{
  "comment": "흥미로운 캐릭터 설정입니다. 병합을 검토해보겠습니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| status | string | Y | 변경된 상태 | `ACCEPTED` |
| reviewed_at | string | Y | 수락 시각 (ISO 8601 UTC, microseconds) | `2024-01-02T10:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "status": "ACCEPTED",
  "reviewed_at": "2024-01-02T10:00:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — 허용되지 않는 상태 전이
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "SUBMITTED 상태의 PR만 수락할 수 있습니다."
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
    "message": "원작자만 PR을 수락할 수 있습니다."
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

## POST /api/v1/pull-requests/{pr_id}/request-changes

관련 페이지: `pages/12-pr-review`

PR에 수정을 요청한다. 상태가 SUBMITTED → CHANGES_REQUESTED로 변경되며, 컨트리뷰터에게 `PR_CHANGES_REQUESTED` 알림이 전송된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/request-changes
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| reason | string | Y | 수정 요청 사유 | `캐릭터의 마법 능력이 기존 규칙과 충돌합니다.` |
| comment | string | N | 추가 코멘트 | `아이디어 자체는 좋습니다.` |

**Request Example**
```json
{
  "reason": "캐릭터의 마법 능력이 기존 규칙과 충돌합니다. 수정 후 재제출해주세요.",
  "comment": "아이디어 자체는 좋습니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| status | string | Y | 변경된 상태 | `CHANGES_REQUESTED` |
| reviewed_at | string | Y | 수정 요청 시각 (ISO 8601 UTC, microseconds) | `2024-01-02T10:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "status": "CHANGES_REQUESTED",
  "reviewed_at": "2024-01-02T10:00:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — 허용되지 않는 상태 전이
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "SUBMITTED 상태의 PR에만 수정을 요청할 수 있습니다."
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
    "message": "원작자만 수정을 요청할 수 있습니다."
  }
}
```

422 Unprocessable Entity — reason 미입력
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "수정 요청 사유를 입력해야 합니다.",
    "details": [
      { "field": "reason", "message": "수정 요청 사유는 필수입니다." }
    ]
  }
}
```

---

## POST /api/v1/pull-requests/{pr_id}/reject

관련 페이지: `pages/12-pr-review`

PR을 거절한다. 상태가 SUBMITTED → REJECTED로 변경된다. RejectReason이 생성되며, 컨트리뷰터에게 `PR_REJECTED` 알림이 전송된다. Reject 사유는 영구 보존된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/reject
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| category | string | Y | 거절 카테고리 (`CONFLICT`, `TOO_VAGUE`, `OUT_OF_SCOPE`, `MISALIGNED`, `DUPLICATE`, `INAPPROPRIATE`, `OTHER`) | `CONFLICT` |
| detail | string | Y | 거절 상세 사유 | `이 설정은 기존 마법 금지 설정과 충돌합니다.` |

**Request Example**
```json
{
  "category": "CONFLICT",
  "detail": "이 설정은 기존 세계관의 마법 금지 설정과 정면으로 충돌합니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| status | string | Y | 변경된 상태 | `REJECTED` |
| reject_reason | object | Y | 생성된 거절 사유 | `{...}` |
| reject_reason.id | integer | Y | RejectReason ID | `1` |
| reject_reason.category | string | Y | 거절 카테고리 | `CONFLICT` |
| reject_reason.detail | string | Y | 거절 상세 사유 | `이 설정은...` |
| reject_reason.created_at | string | Y | 등록 시각 (ISO 8601 UTC) | `2024-01-02T10:00:00Z` |
| reviewed_at | string | Y | 거절 시각 (ISO 8601 UTC, microseconds) | `2024-01-02T10:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "status": "REJECTED",
  "reject_reason": {
    "id": 1,
    "category": "CONFLICT",
    "detail": "이 설정은 기존 세계관의 마법 금지 설정과 정면으로 충돌합니다.",
    "created_at": "2024-01-02T10:00:00Z"
  },
  "reviewed_at": "2024-01-02T10:00:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — 허용되지 않는 상태 전이
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "SUBMITTED 상태의 PR만 거절할 수 있습니다."
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
    "message": "원작자만 PR을 거절할 수 있습니다."
  }
}
```

422 Unprocessable Entity — 필수 필드 누락
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 유효하지 않습니다.",
    "details": [
      { "field": "category", "message": "거절 카테고리는 필수입니다." },
      { "field": "detail", "message": "거절 상세 사유는 필수입니다." }
    ]
  }
}
```

---

## POST /api/v1/pull-requests/{pr_id}/merge

관련 페이지: `pages/12-pr-review`

PR을 공식 작품에 병합한다. 상태가 ACCEPTED 또는 SUBMITTED → MERGED로 변경된다. Merge 행이 생성되고, `citation_url`(퍼머링크)이 발급된다. 컨트리뷰터에게 `PR_MERGED` 알림이 전송되며, ContributorStats와 AuthorStats가 갱신된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/merge
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| credit_text | string | Y | 작품에 표시될 크레딧 문구 (최대 500자) | `아르카의 숨겨진 과거 — 기여: @contributor123` |
| readme_apply_note | string | N | README에 반영할 내용 | `3장 캐릭터 설정에 추가 예정` |
| comment | string | N | 원작자 코멘트 | `훌륭한 기여입니다.` |
| final_grade | string | N | 최종 등급 (`MAJOR`, `NORMAL`, `MINOR`). 없으면 원작자 확정 등급 → AI 등급 순으로 사용 | `MAJOR` |

**Request Example**
```json
{
  "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor123",
  "readme_apply_note": "3장 캐릭터 설정에 추가 예정",
  "comment": "훌륭한 기여입니다. 공식 설정으로 반영합니다.",
  "final_grade": "MAJOR"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| merge_id | integer | Y | Merge ID | `5` |
| pull_request_id | integer | Y | PR ID | `42` |
| status | string | Y | 변경된 상태 | `MERGED` |
| final_grade | string | Y | 최종 등급 | `MAJOR` |
| citation_url | string | Y | 외부 인용 가능한 퍼머링크 URL | `https://worldbuild.example.com/m/5` |
| merged_at | string | Y | 병합 시각 (ISO 8601 UTC, microseconds) | `2024-01-03T12:00:00.000000Z` |

**Success Response Example**

200 OK
```json
{
  "merge_id": 5,
  "pull_request_id": 42,
  "status": "MERGED",
  "final_grade": "MAJOR",
  "citation_url": "https://worldbuild.example.com/m/5",
  "merged_at": "2024-01-03T12:00:00.000000Z"
}
```

**Error Response Example**

400 Bad Request — 허용되지 않는 상태 전이 (예: REJECTED → MERGED)
```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "REJECTED 상태의 PR은 병합할 수 없습니다."
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
    "message": "원작자만 PR을 병합할 수 있습니다."
  }
}
```

422 Unprocessable Entity — credit_text 누락
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 유효하지 않습니다.",
    "details": [
      { "field": "credit_text", "message": "크레딧 문구는 필수입니다." }
    ]
  }
}
```

---

## POST /api/v1/pull-requests/{pr_id}/grade-override

관련 페이지: `pages/12-pr-review`

원작자가 AI 판정 등급을 수동으로 조정한다. AI 등급과 다른 등급을 선택할 경우 `reason`이 필수다. AuditLog(`PR_GRADE_OVERRIDE`)가 기록되며, 컨트리뷰터에게 `GRADE_ADJUSTED` 알림이 전송된다.

**Endpoint**
```
POST /api/v1/pull-requests/{pr_id}/grade-override
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| grade | string | Y | 확정 등급 (`MAJOR`, `NORMAL`, `MINOR`) | `NORMAL` |
| reason | string | 조건부 필수 | 등급 조정 사유. AI 등급과 다를 때 필수 | `전체적으로 좋지만 범위가 좁습니다.` |

**Request Example**
```json
{
  "grade": "NORMAL",
  "reason": "전체적으로 좋은 기여지만 세계관 영향 범위가 생각보다 작습니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| pull_request_id | integer | Y | PR ID | `42` |
| author_grade_override | string | Y | 확정된 등급 | `NORMAL` |
| author_grade_override_reason | string | N | 등급 조정 사유 | `전체적으로 좋은 기여지만...` |

**Success Response Example**

200 OK
```json
{
  "pull_request_id": 42,
  "author_grade_override": "NORMAL",
  "author_grade_override_reason": "전체적으로 좋은 기여지만 세계관 영향 범위가 생각보다 작습니다."
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
    "message": "원작자만 등급을 조정할 수 있습니다."
  }
}
```

422 Unprocessable Entity — AI 등급과 다른데 reason 누락
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "AI 등급과 다른 경우 조정 사유를 입력해야 합니다.",
    "details": [
      { "field": "reason", "message": "AI 등급과 다를 때 reason은 필수입니다." }
    ]
  }
}
```

---

## PATCH /api/v1/pull-requests/{pr_id}/reject-reason

관련 페이지: `pages/12-pr-review`

기존 거절 사유를 수정한다. 기존 RejectReason은 삭제하지 않고 새 행을 추가하며, 기존 행의 `superseded_by_id`에 새 행 ID를 기록한다(체인 방식).

**Endpoint**
```
PATCH /api/v1/pull-requests/{pr_id}/reject-reason
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
| Authorization | string | Y | Bearer access token (원작자만 가능) | `Bearer eyJhbGci...` |
| Content-Type | string | Y | 요청 본문 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| category | string | Y | 새 거절 카테고리 (`CONFLICT`, `TOO_VAGUE`, `OUT_OF_SCOPE`, `MISALIGNED`, `DUPLICATE`, `INAPPROPRIATE`, `OTHER`) | `MISALIGNED` |
| detail | string | Y | 새 거절 상세 사유 | `수정된 거절 사유입니다.` |

**Request Example**
```json
{
  "category": "MISALIGNED",
  "detail": "재검토 결과, 세계관 충돌보다는 원작 방향성과 맞지 않는 점이 더 큰 이유입니다."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| reject_reason | object | Y | 새로 생성된 거절 사유 | `{...}` |
| reject_reason.id | integer | Y | 새 RejectReason ID | `2` |
| reject_reason.category | string | Y | 거절 카테고리 | `MISALIGNED` |
| reject_reason.detail | string | Y | 거절 상세 사유 | `재검토 결과...` |
| reject_reason.superseded_by_id | integer | N | 이 행이 대체된 경우 새 행 ID (현재 최신이면 null) | `null` |
| reject_reason.created_at | string | Y | 등록 시각 (ISO 8601 UTC) | `2024-01-03T09:00:00Z` |

**Success Response Example**

200 OK
```json
{
  "reject_reason": {
    "id": 2,
    "category": "MISALIGNED",
    "detail": "재검토 결과, 세계관 충돌보다는 원작 방향성과 맞지 않는 점이 더 큰 이유입니다.",
    "superseded_by_id": null,
    "created_at": "2024-01-03T09:00:00Z"
  }
}
```

**Error Response Example**

400 Bad Request — REJECTED 상태가 아닌 PR에 사유 수정 시도
```json
{
  "error": {
    "code": "PR_NOT_REJECTED",
    "message": "REJECTED 상태의 PR에만 거절 사유를 수정할 수 있습니다."
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
    "message": "원작자만 거절 사유를 수정할 수 있습니다."
  }
}
```
