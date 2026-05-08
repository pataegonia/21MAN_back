# API 테스트 결과 — 06. Pull Requests 원작자 액션

테스트 일시: 2026-05-09  
서버: `http://127.0.0.1:8000`  
테스트 계정: `testauthor@test.com` (user_id: 1, repo author), `otheruser` (user_id: 2)  
테스트 PR: id=1 (user1 작성), id=2 (user2 작성), id=3 (user2 작성, 테스트용 신규)

---

## 결과 요약

| # | Method | Endpoint | Status | 결과 |
|---|--------|----------|--------|------|
| 1 | POST | `/pull-requests/2/accept` (repo author) | **200** | ✅ |
| 2 | POST | `/pull-requests/2/merge` (ACCEPTED → MERGED) | **200** | ✅ |
| 3 | POST | `/pull-requests/1/request-changes` | **200** | ✅ |
| 4 | POST | `/pull-requests/3/reject` | **200** | ✅ |
| 5 | PATCH | `/pull-requests/3/reject-reason` (수정, 체인) | **200** | ✅ |
| 6 | POST | `/pull-requests/1/grade-override` (동일 등급, reason 불필요) | **200** | ✅ |
| E1 | POST | grade-override — AI 등급과 다른데 reason 없음 | **422** VALIDATION_ERROR | ✅ |
| E2 | POST | accept — 비원작자 접근 | **403** FORBIDDEN | ✅ |
| E3 | POST | accept — 존재하지 않는 PR | **404** PR_NOT_FOUND | ✅ |
| E4 | POST | merge — REJECTED 상태 PR | **400** INVALID_STATUS_TRANSITION | ✅ |
| E5 | POST | accept — 이미 CHANGES_REQUESTED 상태 | **400** INVALID_STATUS_TRANSITION | ✅ |

전체 11개 케이스 통과.

---

## 1. POST `/pull-requests/{pr_id}/accept`

**Request**
```
POST /api/v1/pull-requests/2/accept
Authorization: Bearer eyJhbGci... (user1, repo author)
```
```json
{ "comment": "흥미로운 설정입니다." }
```

**Response**
```json
{
  "pull_request_id": 2,
  "status": "ACCEPTED",
  "reviewed_at": "2026-05-08T16:23:02"
}
```

---

## 2. POST `/pull-requests/{pr_id}/merge`

**Request**
```
POST /api/v1/pull-requests/2/merge
Authorization: Bearer eyJhbGci... (user1, repo author)
```
```json
{
  "credit_text": "아르카의 숨겨진 과거 — 기여: @otheruser",
  "comment": "훌륭한 기여입니다.",
  "final_grade": "MAJOR"
}
```

**Response**
```json
{
  "merge_id": 1,
  "pull_request_id": 2,
  "status": "MERGED",
  "final_grade": "MAJOR",
  "citation_url": "https://worldbuild.example.com/m/1",
  "merged_at": "2026-05-08T16:23:10"
}
```

---

## 3. POST `/pull-requests/{pr_id}/request-changes`

**Response**
```json
{
  "pull_request_id": 1,
  "status": "CHANGES_REQUESTED",
  "reviewed_at": "2026-05-08T16:23:19"
}
```

---

## 4. POST `/pull-requests/{pr_id}/reject`

**Request**
```json
{ "category": "CONFLICT", "detail": "기존 마법 금지 설정과 충돌합니다." }
```

**Response**
```json
{
  "pull_request_id": 3,
  "status": "REJECTED",
  "reject_reason": {
    "id": 1,
    "category": "CONFLICT",
    "detail": "기존 마법 금지 설정과 충돌합니다.",
    "created_at": "2026-05-08T16:23:39"
  },
  "reviewed_at": "2026-05-08T16:23:39"
}
```

---

## 5. PATCH `/pull-requests/{pr_id}/reject-reason`

기존 RejectReason(id=1) 이 superseded 되고 새 행(id=2) 생성됨.

**Response**
```json
{
  "reject_reason": {
    "id": 2,
    "category": "MISALIGNED",
    "detail": "재검토 결과 원작 방향성과 맞지 않습니다.",
    "superseded_by_id": null,
    "created_at": "2026-05-08T16:23:47"
  }
}
```

---

## 6. POST `/pull-requests/{pr_id}/grade-override`

**Request (동일 등급, reason 생략)**
```json
{ "grade": "NORMAL" }
```

**Response**
```json
{
  "pull_request_id": 1,
  "author_grade_override": "NORMAL",
  "author_grade_override_reason": null
}
```

---

## 에러 케이스

### 422 — AI 등급과 다른 등급, reason 없음
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "AI 등급과 다른 경우 조정 사유를 입력해야 합니다." } }
```

### 403 — 비원작자 접근
```json
{ "error": { "code": "FORBIDDEN", "message": "원작자만 PR을 수락할 수 있습니다." } }
```

### 404 — 존재하지 않는 PR
```json
{ "error": { "code": "PR_NOT_FOUND", "message": "존재하지 않는 PR입니다." } }
```

### 400 — 잘못된 상태 전이 (REJECTED → merge)
```json
{ "error": { "code": "INVALID_STATUS_TRANSITION", "message": "REJECTED 상태의 PR은 병합할 수 없습니다." } }
```

### 400 — 잘못된 상태 전이 (CHANGES_REQUESTED → accept)
```json
{ "error": { "code": "INVALID_STATUS_TRANSITION", "message": "SUBMITTED 상태의 PR만 수락할 수 있습니다." } }
```
