# 14 — 내 프로필

## 개요

로그인한 사용자 자신의 프로필 페이지. 공개 프로필(13번)과 동일한 구조이나, 본인만 볼 수 있는 비공개 PR 목록, 전체 PR 현황(DRAFT 포함)이 추가로 표시된다.

---

## 접근 권한

🔑 로그인 사용자 본인

---

## 화면 구성요소

공개 프로필(13번)의 모든 구성요소에 추가하여:

### 프로필 편집 버튼
- "프로필 편집" → 아바타, bio 수정 가능

### 내 PR 목록 탭 (추가)
- 전체 PR 표시 (DRAFT / SUBMITTED / ACCEPTED / CHANGES_REQUESTED / REJECTED / MERGED)
- 상태별 필터 탭
- 각 항목: Repository, PR 제목, 상태 뱃지, 제출일 또는 마지막 저장일
- DRAFT 상태: "작성 계속하기" 버튼 → Draft 작성 페이지

### DRAFT PR 섹션 (별도 강조 표시)
- 작성 중인 PR 목록
- 각 항목: Repository, 마지막 저장일, "계속 작성" 버튼

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 프로필 편집 | 아바타·bio 수정 모달 또는 별도 폼 |
| "작성 계속하기" 클릭 | `/pull-requests/{pr_id}/draft` |
| PR 항목 클릭 | `/pull-requests/{pr_id}` |
| 탭 전환 | 해당 상태 PR만 표시 |

---

## API 연동

### GET /api/v1/auth/me
현재 사용자 정보 (이미 메모리에 있으면 캐시 사용).

### GET /api/v1/users/{username}/pull-requests?page=1&size=20&status=DRAFT
```
Query params:
  status - 상태 필터 (복수 선택 가능: ?status=DRAFT&status=SUBMITTED)
  page, size

Response 200:
{
  "items": [
    {
      "id": 42,
      "repository": { "id": 1, "title": "..." },
      "title": "AI 생성 제목 또는 null",
      "status": "DRAFT",
      "visibility": "PUBLIC",
      "first_drafted_at": "...",
      "last_saved_at": "...",
      "submitted_at": null,
      "ai_grade": null,
      "author_grade_override": null
    }
  ],
  "total": 5
}
```

### PATCH /api/v1/users/{username} (또는 /api/v1/auth/me)
프로필 편집. 본인만 가능.
```
Request:
{
  "avatar": "https://...",
  "bio": "수정된 자기소개"
}

Response 200:
{
  "id": 1,
  "username": "...",
  "avatar": "...",
  "bio": "..."
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| DRAFT PR 없음 | "작성 중인 PR이 없습니다" |
| 제출된 PR 없음 | "아직 제출한 PR이 없습니다" |
| 비공개 PR 있음 | 본인이므로 전체 표시 |

---

## 규칙 및 제약

- `/users/{username}/pull-requests`에서 본인이면 전체(PRIVATE 포함, DRAFT 포함) 조회
- 타인의 프로필에서는 PUBLIC + DRAFT 제외만 표시
- DRAFT 상태 PR은 "내 PR 목록"에만 표시 (공개 프로필에서는 숨김)

---

## 연결 화면

- → Draft 작성 (`/pull-requests/{pr_id}/draft`)
- → PR 상세 (`/pull-requests/{pr_id}`)
- → Repository 상세 (`/repositories/{repo_id}`)
