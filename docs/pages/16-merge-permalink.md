# 16 — Merge 퍼머링크 (/m/{merge_id})

## 개요

병합된 기여의 공개 인용 페이지. 외부에서 링크로 기여 사실을 증명할 수 있도록 영구적으로 제공되는 페이지다. `citation_url`이 이 페이지를 가리킨다.

---

## 접근 권한

🌐 누구나

---

## 화면 구성요소

### 기여 증명 헤더
- "공식 기여로 반영된 작품" 레이블
- 대상 Repository 제목 → `/repositories/{repo_id}`
- 병합 시각 (`merged_at`)
- 영구 인용 URL 복사 버튼

### 기여 내용 섹션
- PR 제목 (AI 생성 제목)
- AI 내용 요약
- 기여 유형 뱃지
- 최종 등급 뱃지 (MAJOR / NORMAL / MINOR)

### 기여자 정보
- 아바타, username → `/users/{username}`
- 크레딧 문구 (`credit_text`)

### 원작자 정보
- 아바타, username → `/users/{username}`
- 원작자 코멘트 (`author_comment`)

### 작성 시점 타임라인
- 첫 작성 시점 (`first_drafted_at`)
- 제출 시점 (`submitted_at`)
- 수락 시점 (있을 경우)
- 병합 시점 (`merged_at`)

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 인용 URL 복사 | 클립보드에 `citation_url` 복사 |
| Repository 링크 클릭 | `/repositories/{repo_id}` 이동 |
| 기여자 프로필 클릭 | `/users/{contributor_username}` |
| 원작자 프로필 클릭 | `/users/{author_username}` |

---

## API 연동

### GET /api/v1/merges/{merge_id}
```
Response 200:
{
  "id": 5,
  "pull_request": {
    "id": 42,
    "title": "마법사 아르카의 숨겨진 과거",
    "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
    "contribution_types": ["character_add"],
    "first_drafted_at": "2024-01-01T00:00:00.000000Z",
    "submitted_at": "2024-01-01T01:00:00.000000Z"
  },
  "repository": {
    "id": 1,
    "title": "내 판타지 세계관",
    "thumbnail": "https://..."
  },
  "contributor": {
    "username": "contributor_name",
    "avatar": "https://..."
  },
  "author": {
    "username": "author_name",
    "avatar": "https://..."
  },
  "final_grade": "MAJOR",
  "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor_name",
  "author_comment": "훌륭한 기여입니다. 공식 설정으로 반영합니다.",
  "citation_url": "https://worldbuild.example.com/m/5",
  "merged_at": "2024-01-03T12:00:00.000000Z"
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| Merge 없음 (404) | "존재하지 않는 기여 기록입니다" |

---

## 규칙 및 제약

- 누구나 접근 가능 (비로그인 포함)
- `citation_url`은 병합 시 서버에서 생성되며 변경되지 않음 (`/m/{merge_id}` 형태)
- 이 페이지는 기여 사실의 외부 인용 및 법적 증명 목적으로 사용될 수 있으므로 삭제 불가
- 타임라인의 모든 시각은 서버 시간 기준 (UTC, ISO 8601)
- 비공개 PR이 병합된 경우에도 이 퍼머링크는 공개 접근 가능 (크레딧 및 증명 목적)

---

## 연결 화면

- → Repository 상세 (`/repositories/{repo_id}`)
- → 기여자 프로필 (`/users/{contributor_username}`)
- → 원작자 프로필 (`/users/{author_username}`)
