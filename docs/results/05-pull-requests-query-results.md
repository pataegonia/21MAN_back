# API 테스트 결과 — 05. Pull Requests 조회

테스트 일시: 2026-05-09  
서버: `http://127.0.0.1:8000`  
테스트 계정: `testauthor@test.com` (user_id: 1, repo author), `otheruser` (user_id: 2)  
테스트 PR: id=1 (user1 작성, PUBLIC), id=2 (user2 작성, PUBLIC)

---

## 결과 요약

| # | Method | Endpoint | Status | 결과 |
|---|--------|----------|--------|------|
| 1 | GET | `/pull-requests/1` (비로그인, PUBLIC) | **200** | ✅ |
| 2 | GET | `/pull-requests/1` (PR 작성자 본인 조회) | **200** | ✅ |
| 3 | GET | `/pull-requests/2` (repo 원작자가 타인 PR 조회 → ViewLog 생성) | **200** | ✅ |
| 4 | GET | `/pull-requests/2` (PR 작성자 조회 → view_log_summary 반환) | **200** | ✅ |
| 5 | GET | `/pull-requests` (목록 — 필터 없음) | **200** | ✅ |
| 6 | GET | `/pull-requests?status=SUBMITTED` | **200** | ✅ |
| 7 | GET | `/pull-requests?grade=NORMAL` | **200** | ✅ |
| 8 | GET | `/pull-requests?repo_id=1` | **200** | ✅ |
| E1 | GET | 존재하지 않는 PR | **404** PR_NOT_FOUND | ✅ |
| E2 | GET | PRIVATE PR — 비로그인 접근 | **403** FORBIDDEN | ✅ |
| E3 | GET | PRIVATE PR — 타인 접근 | **403** FORBIDDEN | ✅ |

전체 11개 케이스 통과.

---

## 1. GET `/pull-requests/{pr_id}` — PR 상세 조회

### 비로그인 (PUBLIC PR) — 200 OK

**Request**
```
GET /api/v1/pull-requests/1
```

**Response**
```json
{
  "id": 1,
  "repository": {
    "id": 1,
    "title": "테스트 판타지 세계관",
    "author": {
      "username": "testauthor"
    }
  },
  "author": {
    "id": 1,
    "username": "testauthor",
    "avatar": null
  },
  "title": "아르카의 금지된 혈통과 새로운 마법 원리",
  "raw_content": "아르카는 사실 마법사 가문의 후손이 아니라 금지된 혈통의 자손이다...",
  "contribution_types": ["character_modify", "lore"],
  "visibility": "PUBLIC",
  "status": "SUBMITTED",
  "contributor_comment": "이 캐릭터의 능력은 기존 마법 체계와 다르게 설계되었으므로 충돌이 없습니다.",
  "author_grade_override": null,
  "author_grade_override_reason": null,
  "author_review_comment": null,
  "changes_requested_reason": null,
  "reject_reason": null,
  "merge_info": null,
  "view_log_summary": null,
  "first_drafted_at": "2026-05-08T15:56:40",
  "submitted_at": "2026-05-08T15:57:39",
  "reviewed_at": null,
  "merged_at": null,
  "created_at": "2026-05-09T00:56:40",
  "updated_at": "2026-05-09T00:57:39"
}
```

### repo 원작자가 타인 PR 조회 → ViewLog + AuditLog 생성 — 200 OK

**Request**
```
GET /api/v1/pull-requests/2
Authorization: Bearer eyJhbGci... (user1, repo author)
```

부가 동작 확인:
- `view_logs` 테이블에 ViewLog 생성 (viewer_id=1, pull_request_id=2)
- `audit_logs` 테이블에 `PR_VIEW` 로그 기록

### PR 작성자(user2) 본인 조회 → view_log_summary 반환 — 200 OK

**Request**
```
GET /api/v1/pull-requests/2
Authorization: Bearer eyJhbGci... (user2, PR author)
```

**Response (일부)**
```json
{
  "view_log_summary": {
    "total_views": 1,
    "first_viewed_at": "2026-05-08T16:08:29"
  }
}
```

---

## 2. GET `/pull-requests` — PR 목록

### 필터 없음 — 200 OK

**Request**
```
GET /api/v1/pull-requests
```

**Response**
```json
{
  "items": [
    {
      "id": 1,
      "repository": {
        "id": 1,
        "title": "테스트 판타지 세계관"
      },
      "author": {
        "username": "testauthor",
        "avatar": null
      },
      "title": "아르카의 금지된 혈통과 새로운 마법 원리",
      "status": "SUBMITTED",
      "visibility": "PUBLIC",
      "contribution_types": ["character_modify", "lore"],
      "ai_grade": "NORMAL",
      "submitted_at": "2026-05-08T15:57:39"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

### 필터 테스트

| 필터 | 요청 | 결과 |
|------|------|------|
| `status=SUBMITTED` | `?status=SUBMITTED` | total=1 ✅ |
| `grade=NORMAL` | `?grade=NORMAL` | total=1, ai_grade=NORMAL ✅ |
| `repo_id=1` | `?repo_id=1` | total=1 ✅ |

---

## 에러 케이스

### 404 — 존재하지 않는 PR
```json
{ "error": { "code": "PR_NOT_FOUND", "message": "존재하지 않는 PR입니다." } }
```

### 403 — PRIVATE PR 비로그인 접근
```json
{ "error": { "code": "FORBIDDEN", "message": "열람 권한이 없습니다." } }
```

### 403 — PRIVATE PR 타인 접근
```json
{ "error": { "code": "FORBIDDEN", "message": "열람 권한이 없습니다." } }
```
