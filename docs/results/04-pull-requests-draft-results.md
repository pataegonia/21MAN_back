# API 테스트 결과 — 04. Pull Requests Draft & 작성

테스트 일시: 2026-05-09  
서버: `http://127.0.0.1:8000`  
테스트 계정: `testauthor@test.com` (user_id: 1)  
테스트 Repository: id=1, title="테스트 판타지 세계관"

---

## 결과 요약

| # | Method | Endpoint | Status | 결과 |
|---|--------|----------|--------|------|
| 1 | POST | `/repositories/1/pull-requests/draft` (신규) | **201** | ✅ |
| 2 | POST | `/repositories/1/pull-requests/draft` (기존) | **200** | ✅ |
| 3 | GET | `/pull-requests/1/draft` | **200** | ✅ |
| 4 | PATCH | `/pull-requests/1/draft` | **200** | ✅ |
| 5 | POST | `/pull-requests/1/ai-analyze` | **200** | ✅ |
| 6 | GET | `/pull-requests/1/ai-analysis` | **200** | ✅ |
| 7 | GET | `/pull-requests/1/ai-analysis?run_seq=1` | **200** | ✅ |
| 8 | POST | `/pull-requests/1/submit` | **200** | ✅ |
| 9 | PATCH | `/pull-requests/1/contributor-comment` | **200** | ✅ |
| E1 | POST | 토큰 없음 | **401** INVALID_TOKEN | ✅ |
| E2 | POST | 존재하지 않는 Repository | **404** REPOSITORY_NOT_FOUND | ✅ |
| E3 | GET | 존재하지 않는 PR | **404** PR_NOT_FOUND | ✅ |
| E4 | PATCH | SUBMITTED PR에 저장 시도 | **400** PR_NOT_DRAFT | ✅ |
| E5 | GET | 타인 PR 접근 | **403** FORBIDDEN | ✅ |

전체 14개 케이스 통과.

---

## 1. POST `/repositories/{repo_id}/pull-requests/draft`

### 신규 생성 — 201 Created

**Request**
```
POST /api/v1/repositories/1/pull-requests/draft
Authorization: Bearer eyJhbGci...
```

**Response**
```json
{
  "pull_request_id": 1,
  "first_drafted_at": "2026-05-08T15:56:40",
  "last_saved_at": "2026-05-08T15:56:40",
  "save_count": 0,
  "raw_content": null
}
```

### 기존 Draft 반환 — 200 OK

동일 요청 재호출 시 기존 PR id 반환, 상태 코드 200.

```json
{
  "pull_request_id": 1,
  "first_drafted_at": "2026-05-08T15:56:40",
  "last_saved_at": "2026-05-08T15:56:40",
  "save_count": 0,
  "raw_content": null
}
```

---

## 2. GET `/pull-requests/{pr_id}/draft`

**Response — 200 OK**
```json
{
  "pull_request_id": 1,
  "repository": {
    "id": 1,
    "title": "테스트 판타지 세계관"
  },
  "first_drafted_at": "2026-05-08T15:56:40",
  "last_saved_at": "2026-05-08T15:56:40",
  "save_count": 0,
  "raw_content": null,
  "latest_ai_analysis": null
}
```

---

## 3. PATCH `/pull-requests/{pr_id}/draft`

**Request Body**
```json
{
  "raw_content": "아르카는 사실 마법사 가문의 후손이 아니라 금지된 혈통의 자손이다..."
}
```

**Response — 200 OK**
```json
{
  "pull_request_id": 1,
  "last_saved_at": "2026-05-08T15:56:51",
  "save_count": 1
}
```

---

## 4. POST `/pull-requests/{pr_id}/ai-analyze`

OpenAI `gpt-4o-2024-08-06` 호출. 실제 분석 결과 반환.

**Response — 200 OK**
```json
{
  "id": 1,
  "pull_request_id": 1,
  "run_seq": 1,
  "generated_title": "아르카의 금지된 혈통과 새로운 마법 원리",
  "summary": "아르카는 금지된 혈통의 자손으로, 기존 마법 체계와 다른 원리로 작동하는 능력을 지니고 있다. 이는 세계관의 마법 법칙에 새로운 예외를 도입한다.",
  "structured_content": {
    "character": {
      "name": "아르카",
      "lineage": "금지된 혈통",
      "magic_system": "기존과 다른 원리",
      "impact": "마법 법칙에 새로운 예외 추가"
    }
  },
  "contribution_types": ["character_modify", "lore"],
  "score_scope": 6,
  "score_permanence": 7,
  "score_cascade": 8,
  "score_alignment": 5,
  "score_specificity": 7,
  "score_total": 33,
  "ai_grade": "NORMAL",
  "rationale": "아르카의 새로운 혈통과 마법 원리는 기존 마법 체계에 큰 변화를 주며, 세계관의 법칙에 예외를 추가하여 파급 효과가 크다. 그러나 기존 설정과의 정합성에서 일부 충돌 가능성이 있다.",
  "missing_info": [
    "아르카의 구체적인 능력 설명",
    "금지된 혈통의 역사 및 배경"
  ],
  "conflict_checks": [
    {
      "risk_level": "MEDIUM",
      "check_target": "contribution_guideline",
      "passed": false,
      "detail": "기존 세계관과의 충돌 가능성이 있으며, 기여 가이드라인을 위반할 수 있음"
    }
  ],
  "model_name": "gpt-4o-2024-08-06",
  "created_at": "2026-05-08T15:57:21"
}
```

---

## 5. GET `/pull-requests/{pr_id}/ai-analysis`

### 최신 회차 조회 — 200 OK

`GET /api/v1/pull-requests/1/ai-analysis` → run_seq=1 반환 (위 결과와 동일)

### 특정 회차 조회 — 200 OK

`GET /api/v1/pull-requests/1/ai-analysis?run_seq=1` → 동일 결과 반환

---

## 6. POST `/pull-requests/{pr_id}/submit`

**Request Body**
```json
{ "visibility": "PUBLIC" }
```

**Response — 200 OK**
```json
{
  "pull_request_id": 1,
  "status": "SUBMITTED",
  "visibility": "PUBLIC",
  "submitted_at": "2026-05-08T15:57:39"
}
```

부가 동작 확인:
- `notifications` 테이블에 `PR_SUBMITTED` 알림 생성 (recipient_id=1, repo author)
- `audit_logs` 테이블에 `PR_SUBMIT` 로그 기록

---

## 7. PATCH `/pull-requests/{pr_id}/contributor-comment`

**Request Body**
```json
{
  "contributor_comment": "이 캐릭터의 능력은 기존 마법 체계와 다르게 설계되었으므로 충돌이 없습니다."
}
```

**Response — 200 OK**
```json
{
  "pull_request_id": 1,
  "contributor_comment": "이 캐릭터의 능력은 기존 마법 체계와 다르게 설계되었으므로 충돌이 없습니다."
}
```

---

## 에러 케이스

### 401 — 토큰 없음
```json
{ "error": { "code": "INVALID_TOKEN", "message": "Missing access token" } }
```

### 404 — 존재하지 않는 Repository
```json
{ "error": { "code": "REPOSITORY_NOT_FOUND", "message": "존재하지 않는 Repository입니다." } }
```

### 404 — 존재하지 않는 PR
```json
{ "error": { "code": "PR_NOT_FOUND", "message": "존재하지 않는 PR입니다." } }
```

### 400 — SUBMITTED PR에 저장 시도
```json
{ "error": { "code": "PR_NOT_DRAFT", "message": "DRAFT 상태의 PR만 저장할 수 있습니다." } }
```

### 400 — 재제출 시도 (DRAFT 아닌 PR 제출)
```json
{ "error": { "code": "INVALID_STATUS_TRANSITION", "message": "DRAFT 상태의 PR만 제출할 수 있습니다." } }
```

### 403 — 타인 PR 접근
```json
{ "error": { "code": "FORBIDDEN", "message": "본인의 Draft만 조회할 수 있습니다." } }
```
