# 11 — PR 상세

## 개요

제출된 PR의 전체 내용을 보여주는 페이지. 접근 권한에 따라 표시 영역이 다르다. 원작자가 이 페이지를 열람하면 ViewLog가 자동으로 생성된다.

---

## 접근 권한

| 기능 | 권한 |
|------|------|
| PUBLIC PR 조회 | 🌐 누구나 |
| PRIVATE PR 조회 | ✍️ 작성자 + 👑 원작자 |
| AI 분석 결과 | ✍️ 작성자 + 👑 원작자 |
| ViewLog 열람 기록 확인 | ✍️ 작성자 (자신의 PR이 언제 열람됐는지 확인) |
| 원작자 검토 액션 패널 | 👑 원작자 |
| Reject 사유 조회 | ✍️ 작성자 + 👑 원작자 |

---

## 화면 구성요소

### 헤더 영역
- PR 제목 (AI 생성 제목 또는 "분석 전" 표시)
- 상태 뱃지: DRAFT / SUBMITTED / ACCEPTED / CHANGES_REQUESTED / REJECTED / MERGED
- 작성자 정보 (아바타, username) → `/users/{username}`
- 대상 Repository → `/repositories/{repo_id}`
- 첫 작성 시점 (`first_drafted_at`)
- 제출 시점 (`submitted_at`)
- 공개 여부 (PUBLIC / PRIVATE)
- 기여 유형 뱃지 목록

### 원문 섹션
- `raw_content` 전체 표시

### AI 분석 결과 섹션 (작성자 + 원작자만)
- AI 생성 제목
- 내용 요약
- 5축 점수 시각화 (막대 또는 레이더)
- AI 등급 (+ 원작자 확정 등급이 있으면 함께 표시)
- 충돌 검사 결과
- 누락 정보 목록
- 분석 근거
- 재분석 회차 선택 (복수 분석 시)

### 컨트리뷰터 의견 섹션
- `contributor_comment` 표시
- 작성자 본인이면 "수정" 버튼 (DRAFT 상태일 때만)

### 열람 기록 섹션 (작성자 본인만)
- "원작자 열람 기록" 헤더
- 열람 횟수 + 최초 열람 시각
- "원작자가 아직 열람하지 않았습니다" (ViewLog 없을 때)

### 원작자 확정 등급 섹션 (있을 때)
- 원작자 확정 등급 뱃지
- AI 등급과 다른 경우: 조정 사유 표시

### Reject 사유 섹션 (REJECTED 상태)
- 카테고리 + 상세 사유
- 사유 변경 이력 (체인 표시)

### 원작자 검토 액션 패널 (👑 원작자, SUBMITTED 또는 ACCEPTED 상태)
- 상세 설명: 12-pr-review 참조

### Merge 정보 섹션 (MERGED 상태)
- 최종 등급
- 크레딧 문구
- 원작자 코멘트
- 병합 시각
- 퍼머링크 (`/m/{merge_id}`)

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| AI 분석 회차 선택 | 해당 분석 결과로 전환 |
| 원작자 열람 기록 확인 | 열람 기록 섹션 표시 (작성자만) |
| Reject 사유 이력 보기 | 변경 이력 체인 펼치기 |
| Merge 퍼머링크 복사 | 클립보드에 URL 복사 |

---

## API 연동

### GET /api/v1/pull-requests/{pr_id}
```
Response 200:
{
  "id": 42,
  "repository": { "id": 1, "title": "...", "author": { "username": "..." } },
  "author": { "id": 1, "username": "...", "avatar": "..." },
  "title": "AI 생성 제목",
  "raw_content": "...",
  "contribution_types": ["character_add"],
  "visibility": "PUBLIC",
  "status": "SUBMITTED",
  "contributor_comment": "...",
  "author_grade_override": null,
  "author_grade_override_reason": null,
  "author_review_comment": null,
  "changes_requested_reason": null,
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "submitted_at": "2024-01-01T01:00:00.000000Z",
  "reviewed_at": null,
  "merged_at": null,
  "created_at": "...",
  "updated_at": "..."
}
```

**ViewLog 자동 생성 조건:**
- `viewer == repo.author` AND `viewer != pr.author`
- 조건 충족 시 서버가 ViewLog INSERT + AuditLog(PR_VIEW) 처리

### GET /api/v1/pull-requests/{pr_id}/ai-analysis
분석 결과 조회 (작성자 + 원작자만).

---

## ViewLog 관련 규칙 (무결성 요건 5.2)

- 원작자가 PR을 열람할 때마다 ViewLog 행이 자동 INSERT됨
- 서비스 레이어에서 ViewLog UPDATE/DELETE를 절대 호출하지 않음
- 같은 PR을 여러 번 열람해도 매번 별도 행이 생성됨
- PR 작성자 본인이 조회하는 경우에는 ViewLog를 생성하지 않음
- ViewLog 항목: `pull_request_id`, `viewer_id`, `viewed_at`, `ip_hash`, `day_bucket_hash`

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| PR 없음 (404) | "존재하지 않는 PR입니다" |
| PRIVATE PR 권한 없음 (403) | "열람 권한이 없습니다" |
| AI 분석 없음 | AI 분석 섹션에 "아직 분석 결과가 없습니다" |

---

## 규칙 및 제약

- PUBLIC PR: 비로그인 사용자도 열람 가능 (ViewLog는 로그인한 원작자에게만 생성)
- PRIVATE PR: 작성자와 원작자만 열람 가능
- 상태별 표시 차이:
  - DRAFT: 작성자 본인만 접근 가능
  - SUBMITTED 이후: 위 권한 매트릭스 적용

---

## 연결 화면

- → 사용자 프로필 (`/users/{username}`)
- → Repository 상세 (`/repositories/{repo_id}`)
- → Merge 퍼머링크 (`/m/{merge_id}`) — MERGED 상태
- → 원작자 검토 액션 (`12-pr-review` — 같은 페이지의 패널)
