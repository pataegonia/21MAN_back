# 05 — Repository 상세

## 개요

작품의 세계관, 캐릭터, 모집 영역, 기여 이력을 보여주는 상세 페이지. 컨트리뷰터 모집의 핵심 진입점이다.

---

## 접근 권한

| 기능 | 권한 |
|------|------|
| 기본 정보 · README 조회 | 🌐 누구나 |
| Merge 이력 · 기여자 목록 | 🌐 누구나 |
| PR 목록 | 🌐+ (PUBLIC만) / 👑 전체 |
| Repository 통계 | 👑 원작자만 |
| 수정 버튼 노출 | 👑 원작자만 |
| "기여하기" 버튼 | 🔑 로그인 사용자 |

---

## 화면 구성요소

### 헤더 영역
- 썸네일
- 제목
- 원작자 정보 (아바타, username) → 클릭 시 `/users/{username}`
- 태그 목록
- 외부 링크 (원작 플랫폼 등)
- 생성일 / 최근 수정일
- 원작자에게만 표시: "수정하기" 버튼, Repository 통계 요약

### 탭 네비게이션
- README
- Merge 이력
- 기여자

### README 탭
- 작품 설명 (마크다운 렌더링)
- 주요 캐릭터 목록 (이름, 설명)
- 주요 지역·장소 목록
- 핵심 세계관 규칙 목록
- 금지 설정 목록
- 모집 중인 기여 영역 (뱃지/칩 형태)
- 기여 가이드라인

### Merge 이력 탭
- Merge된 PR 목록
- 각 항목: 기여자, PR 제목, 최종 등급(MAJOR/NORMAL/MINOR), 병합일
- 클릭 시 `/m/{merge_id}` 또는 `/pull-requests/{pr_id}`

### 기여자 탭
- Merge 기여자 집계 목록
- 각 항목: 아바타, username, Major/Normal/Minor 수, 총 기여 수
- 클릭 시 `/users/{username}`

### CTA 영역
- "이 작품에 기여하기" 버튼 → Draft 생성 후 `/pull-requests/{pr_id}/draft`
- 비로그인: "로그인 후 기여하기" → `/login`

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 탭 전환 | 해당 탭 데이터 조회 |
| 기여하기 클릭 | Draft 생성 → PR 작성 페이지 |
| 수정하기 클릭 (원작자) | `/repositories/{repo_id}/edit` |
| 기여자 클릭 | `/users/{username}` |
| Merge 이력 클릭 | PR 상세 또는 Merge 퍼머링크 |

---

## API 연동

### GET /api/v1/repositories/{repo_id}
```
Response 200:
{
  "id": 1,
  "title": "...",
  "description": "...",
  "thumbnail": "...",
  "tags": ["..."],
  "external_links": ["https://..."],
  "author": { "id": 1, "username": "...", "avatar": "..." },
  "readme": {
    "content": "...",
    "characters": [{ "name": "...", "description": "..." }],
    "regions": [{ "name": "...", "description": "..." }],
    "world_rules": ["..."],
    "forbidden_settings": ["..."]
  },
  "recruiting_areas": ["character_add", "worldbuilding"],
  "contribution_guidelines": "...",
  "merge_count": 5,
  "pr_count": 12,
  "created_at": "...",
  "updated_at": "..."
}
```

### GET /api/v1/repositories/{repo_id}/merges?page=1&size=20
```
Response 200:
{
  "items": [
    {
      "id": 1,
      "pull_request": { "id": 1, "title": "..." },
      "contributor": { "username": "...", "avatar": "..." },
      "final_grade": "MAJOR",
      "credit_text": "...",
      "merged_at": "..."
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20
}
```

### GET /api/v1/repositories/{repo_id}/contributors
```
Response 200:
{
  "contributors": [
    {
      "user": { "username": "...", "avatar": "..." },
      "major_count": 2,
      "normal_count": 3,
      "minor_count": 1,
      "total_count": 6
    }
  ]
}
```

### POST /api/v1/repositories/{repo_id}/pull-requests/draft
"기여하기" 클릭 시 호출. 이미 DRAFT 상태 PR이 있으면 기존 PR id 반환.
```
Response 201:
{
  "pull_request_id": 42,
  "first_drafted_at": "2024-01-01T00:00:00.000000Z"
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| Repository 없음 (404) | "존재하지 않는 작품입니다" |
| Merge 이력 없음 | "아직 반영된 기여가 없습니다" |
| 기여자 없음 | "아직 기여자가 없습니다" |

---

## 규칙 및 제약

- "기여하기" 클릭 시 같은 Repository에 이미 DRAFT PR이 있으면 새로 생성하지 않고 기존 PR로 이동
- `first_drafted_at`은 서버 시간으로 최초 1회만 기록됨 (이후 자동 저장에서 변경 불가)

---

## 연결 화면

- → PR 작성 (`/pull-requests/{pr_id}/draft`)
- → Repository 수정 (`/repositories/{repo_id}/edit`) — 원작자만
- → 사용자 프로필 (`/users/{username}`)
- → Merge 퍼머링크 (`/m/{merge_id}`)
