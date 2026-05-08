# 08 — PR 작성 (Draft + 자동저장)

## 개요

컨트리뷰터가 아이디어를 자유롭게 작성하는 에디터 페이지. 최초 진입 시 Draft가 생성되어 `first_drafted_at`이 서버 시간으로 영구 기록된다. 이후 30초마다 자동 저장된다.

---

## 접근 권한

✍️ Draft를 소유한 컨트리뷰터 본인만

---

## 화면 구성요소

### 상단 정보바
- 대상 Repository 제목 + 링크
- 첫 작성 시점 표시 (`first_drafted_at`)
- 마지막 저장 시각 (`last_saved_at`)
- 저장 횟수 (`save_count`)
- 자동저장 상태 인디케이터 (저장 중 / 저장됨 / 저장 실패)

### 작성 영역
- 제목 없음 — AI가 생성
- 자유 작성 텍스트 에디터 (`raw_content`)
  - 최소 줄 수 제한 없음
  - 마크다운 또는 일반 텍스트

### 우측 패널 (또는 하단)
- "AI 분석 요청" 버튼
  - 비활성: raw_content 없을 때
  - 분석 중 로딩 스피너
  - 완료 후 "AI 분석 결과 보기" 버튼 표시
- AI 분석 결과 요약 (있을 경우): 등급, 총점, 충돌 위험도

### 하단 액션바
- "임시 저장" 수동 버튼
- "제출하기" 버튼 → AI 분석 완료 후에만 활성화 (또는 경고와 함께 허용)

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 페이지 최초 진입 | Draft 생성 API 호출 → `first_drafted_at` 서버 시간으로 기록 (재진입 시 기존 PR 로드) |
| 텍스트 입력 | 로컬 상태 업데이트, 30초 뒤 자동저장 타이머 리셋 |
| 자동저장 (30초마다) | PATCH /draft → `last_saved_at`, `save_count` 갱신 |
| 수동 저장 버튼 | 즉시 PATCH /draft |
| AI 분석 요청 | POST /ai-analyze → 완료 후 분석 결과 패널 표시 |
| 제출하기 | PR 제출 페이지(10번)로 이동 |

---

## API 연동

### POST /api/v1/repositories/{repo_id}/pull-requests/draft
Repository 상세에서 "기여하기" 클릭 시 호출. 같은 repo+author 조합 DRAFT가 이미 있으면 기존 id 반환.
```
Header: Authorization: Bearer {access_token}

Response 201:
{
  "pull_request_id": 42,
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "last_saved_at": "2024-01-01T00:00:00.000000Z",
  "save_count": 0,
  "raw_content": null
}
```

### GET /api/v1/pull-requests/{pr_id}/draft
재진입 시 기존 초안 로드.
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "pull_request_id": 42,
  "repository": { "id": 1, "title": "..." },
  "first_drafted_at": "2024-01-01T00:00:00.000000Z",
  "last_saved_at": "2024-01-01T00:05:00.000000Z",
  "save_count": 10,
  "raw_content": "아이디어 내용...",
  "latest_ai_analysis": null
}
```

### PATCH /api/v1/pull-requests/{pr_id}/draft
자동저장 또는 수동 저장.
```
Header: Authorization: Bearer {access_token}

Request:
{
  "raw_content": "작성 중인 내용..."
}

Response 200:
{
  "pull_request_id": 42,
  "last_saved_at": "2024-01-01T00:05:30.000000Z",
  "save_count": 11
}
```

**중요:** 서버는 `first_drafted_at`을 절대 갱신하지 않는다.

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| Draft 없음 (신규) | POST /draft 자동 호출 |
| 자동저장 실패 | 저장 상태 인디케이터에 "저장 실패" 표시, 재시도 버튼 |
| 페이지 이탈 시 미저장 내용 있음 | "저장되지 않은 내용이 있습니다" 확인 다이얼로그 |

---

## 규칙 및 제약

- `first_drafted_at`은 최초 Draft 생성 시 **서버 시간**으로 기록, 이후 불변
- 클라이언트가 보낸 시각 값은 신뢰하지 않음
- 자동저장은 `raw_content`, `last_saved_at`, `save_count`만 갱신
- 같은 Repository에 동일 사용자의 DRAFT는 1개만 허용 (application-level 가드)
- DRAFT 상태 PR만 자동저장 가능 (SUBMITTED 이후에는 draft 엔드포인트 호출 차단)

---

## 연결 화면

- "AI 분석 요청" 완료 → 09-pr-ai-analysis 패널이 같은 페이지에 표시
- "제출하기" 클릭 → 10-pr-submit
- 대상 Repository 링크 → `/repositories/{repo_id}`
