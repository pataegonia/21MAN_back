# 12 — 원작자 검토 액션

## 개요

PR 상세 페이지 내 원작자 전용 검토 패널. 수락, 수정 요청, 거절, 병합, 등급 조정 액션을 수행한다. 모든 액션은 AuditLog에 기록된다.

---

## 접근 권한

👑 해당 Repository의 원작자만

---

## 화면 구성요소

### 액션 패널 (현재 PR 상태에 따라 노출 제어)

#### SUBMITTED 상태에서 표시되는 액션
- **수락** 버튼 + 선택적 코멘트 입력
- **수정 요청** 버튼 + 사유 입력 (필수) + 코멘트 입력
- **거절** 버튼 + 카테고리 선택 (필수) + 상세 사유 입력 (필수)

#### ACCEPTED 상태에서 표시되는 액션
- **병합** 버튼 + 크레딧 문구 (필수) + README 반영 내용 + 코멘트 + 최종 등급 선택
- **등급 조정** 버튼

#### 등급 조정 (SUBMITTED 또는 ACCEPTED 상태)
- 현재 AI 등급 표시
- 원작자 확정 등급 선택: MAJOR / NORMAL / MINOR
- AI 등급과 다를 때 조정 사유 입력 (필수)

### 검토 이력 타임라인
- 과거 액션들의 시간 순 목록
- 각 항목: 액션 유형, 시각, 코멘트 or 사유

---

## 사용자 액션 및 상태 전이

| 액션 | 필요 정보 | 상태 전이 | 알림 |
|------|-----------|-----------|------|
| 수락 | 코멘트(선택) | SUBMITTED → ACCEPTED | 컨트리뷰터: PR_ACCEPTED |
| 수정 요청 | 사유(필수), 코멘트(선택) | SUBMITTED → CHANGES_REQUESTED | 컨트리뷰터: PR_CHANGES_REQUESTED |
| 거절 | 카테고리(필수), 상세 사유(필수) | SUBMITTED → REJECTED | 컨트리뷰터: PR_REJECTED |
| 병합 | 크레딧 문구(필수), README 반영 내용(선택), 코멘트(선택) | ACCEPTED → MERGED | 컨트리뷰터: PR_MERGED |
| 등급 조정 | 등급(필수), 사유(AI 등급과 다를 때 필수) | 상태 변경 없음 | 컨트리뷰터: GRADE_ADJUSTED |
| Reject 사유 수정 | 카테고리(필수), 상세 사유(필수) | 상태 변경 없음 | — |

---

## API 연동

### POST /api/v1/pull-requests/{pr_id}/accept
```
Header: Authorization: Bearer {access_token}

Request:
{
  "comment": "흥미로운 캐릭터 설정입니다. 병합을 검토해보겠습니다."
}

Response 200:
{
  "pull_request_id": 42,
  "status": "ACCEPTED",
  "reviewed_at": "2024-01-02T10:00:00.000000Z"
}
```

### POST /api/v1/pull-requests/{pr_id}/request-changes
```
Request:
{
  "reason": "캐릭터의 마법 능력이 기존 규칙과 충돌합니다. 수정 후 재제출해주세요.",
  "comment": "아이디어 자체는 좋습니다."
}

Response 200:
{
  "pull_request_id": 42,
  "status": "CHANGES_REQUESTED",
  "reviewed_at": "..."
}
```

### POST /api/v1/pull-requests/{pr_id}/reject
```
Request:
{
  "category": "CONFLICT",
  "detail": "이 설정은 기존 세계관의 마법 금지 설정과 정면으로 충돌합니다."
}

Response 200:
{
  "pull_request_id": 42,
  "status": "REJECTED",
  "reject_reason": {
    "id": 1,
    "category": "CONFLICT",
    "detail": "...",
    "created_at": "..."
  }
}
```

### POST /api/v1/pull-requests/{pr_id}/merge
```
Request:
{
  "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor_name",
  "readme_apply_note": "3장 캐릭터 설정에 추가 예정",
  "comment": "훌륭한 기여입니다. 공식 설정으로 반영합니다.",
  "final_grade": "MAJOR"
}

Response 200:
{
  "merge_id": 5,
  "pull_request_id": 42,
  "status": "MERGED",
  "merged_at": "2024-01-03T12:00:00.000000Z",
  "citation_url": "https://worldbuild.example.com/m/5"
}
```

**서버 처리 순서:**
1. PR 상태 → MERGED
2. Merge 행 생성 (`citation_url = /m/{merge_id}`)
3. ContributorStats 갱신
4. AuthorStats 갱신
5. 컨트리뷰터 알림(`PR_MERGED`)
6. AuditLog(`PR_MERGE`)

### POST /api/v1/pull-requests/{pr_id}/grade-override
```
Request:
{
  "grade": "NORMAL",
  "reason": "전체적으로 좋은 기여지만 세계관 영향 범위가 생각보다 작습니다."
}
```
AI 등급과 동일한 등급을 선택해도 요청 가능. AI 등급과 다를 때만 `reason` 필수.

```
Response 200:
{
  "pull_request_id": 42,
  "author_grade_override": "NORMAL",
  "author_grade_override_reason": "..."
}
```

### PATCH /api/v1/pull-requests/{pr_id}/reject-reason
기존 Reject 사유를 수정할 때 사용. 기존 행은 supersede되고 새 행이 추가된다.
```
Request:
{
  "category": "MISALIGNED",
  "detail": "수정된 거절 사유입니다."
}

Response 200:
{
  "reject_reason": {
    "id": 2,
    "category": "MISALIGNED",
    "detail": "...",
    "superseded_by_id": null,
    "created_at": "..."
  }
}
```

---

## Reject 카테고리 목록

| 코드 | 설명 |
|------|------|
| `CONFLICT` | 기존 세계관과 충돌 |
| `TOO_VAGUE` | 기여 내용이 너무 모호함 |
| `OUT_OF_SCOPE` | 모집 영역과 맞지 않음 |
| `MISALIGNED` | 원작 방향성과 맞지 않음 |
| `DUPLICATE` | 이미 존재하는 설정과 중복 |
| `INAPPROPRIATE` | 부적절한 내용 |
| `OTHER` | 기타 |

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 허용되지 않는 상태 전이 | 422 — "현재 상태에서 해당 액션을 수행할 수 없습니다" |
| 거절 사유 미입력 | "거절 사유를 반드시 입력해야 합니다" |
| 등급 조정 사유 미입력 (AI 등급과 다를 때) | "AI 등급과 다른 경우 조정 사유를 입력해야 합니다" |
| 크레딧 문구 미입력 (병합 시) | "크레딧 문구를 입력해야 합니다" |

---

## 규칙 및 제약

### 상태 전이 가드 (서비스 레이어에서 강제)
허용:
- DRAFT → SUBMITTED
- SUBMITTED → ACCEPTED / CHANGES_REQUESTED / REJECTED / MERGED
- ACCEPTED → MERGED
- CHANGES_REQUESTED → SUBMITTED

금지:
- REJECTED → MERGED
- MERGED → 모든 상태

### Reject 사유 보존 (무결성 요건 5.3)
- RejectReason 행은 DELETE 불가
- 사유 변경 시 기존 행에 `superseded_by_id` 채우고 새 행 INSERT
- 컨트리뷰터는 언제든 자신의 PR Reject 사유 전체 이력 조회 가능

### 최종 등급 결정 규칙
- Merge 시 `final_grade`: 원작자 확정 등급(`author_grade_override`)이 있으면 사용, 없으면 AI 등급 사용

### 모든 액션은 AuditLog에 기록됨
PR_ACCEPT / PR_REQUEST_CHANGES / PR_REJECT / PR_MERGE / PR_GRADE_OVERRIDE

---

## 연결 화면

- 수락 후 → PR 상세 (상태: ACCEPTED)
- 거절 후 → PR 상세 (상태: REJECTED)
- 병합 후 → PR 상세 (상태: MERGED) + Merge 퍼머링크 안내
