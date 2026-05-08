# 09 — PR AI 분석

## 개요

컨트리뷰터가 요청한 AI 분석 결과를 보여주는 패널/섹션. Draft 작성 페이지(08)에 포함되거나 별도 탭으로 제공될 수 있다. 원작자도 PR 상세에서 분석 결과를 확인한다.

---

## 접근 권한

| 기능 | 권한 |
|------|------|
| AI 분석 요청 | ✍️ Draft 소유 컨트리뷰터 |
| 분석 결과 조회 | ✍️ 컨트리뷰터 본인 + 👑 원작자 |

---

## 화면 구성요소

### AI 분석 요청 버튼
- `raw_content` 없을 때 비활성
- 클릭 시 로딩 스피너 + "AI가 분석 중입니다..." 메시지
- 완료 후 분석 결과 패널로 전환

### 분석 결과 패널

#### 요약 섹션
- AI 생성 제목 (`generated_title`)
- 내용 요약 (`summary`)
- 기여 유형 뱃지 목록 (`contribution_types`)

#### 5축 점수 섹션
| 항목 | 점수 | 설명 |
|------|------|------|
| Scope | 0~10 | 작품에 영향을 미치는 범위 |
| Permanence | 0~10 | 설정의 장기적 지속성 |
| Cascade | 0~10 | 다른 설정에 연쇄 영향 |
| Alignment | 0~10 | 기존 세계관과의 정합성 |
| Specificity | 0~10 | 제안의 구체성·실행 가능성 |

- 총점: 0~50점
- 막대 그래프 또는 레이더 차트로 시각화

#### 등급 섹션
- AI 판정 등급: `MAJOR` / `NORMAL` / `MINOR` (뱃지)
- 등급 기준 안내 툴팁

#### 충돌 검사 섹션
- 전체 위험도: `LOW` / `MEDIUM` / `HIGH`
- 항목별 체크 결과 (통과 ✓ / 주의 ⚠ / 충돌 ✕)
  - README 일치
  - 캐릭터 설정
  - 지역 설정
  - 세계관 규칙
  - 금지 설정
  - 최근 Merge된 PR
  - 유사한 기존 PR
- 각 항목별 상세 설명

#### 누락 정보 섹션
- AI가 파악한 누락 또는 보완 필요 항목 목록

#### 분석 근거 섹션
- AI가 판단한 근거 텍스트 (`rationale`)

#### 분석 메타 정보
- 사용 모델명 (`model_name`)
- 분석 일시 (`created_at`)
- 분석 회차 (`run_seq`)
- 이전 분석 조회 링크 (재분석한 경우)

### 재분석 버튼
- "다시 분석 요청" — 클릭 시 새 AiAnalysis 행 생성 (run_seq +1)
- 이전 분석 결과는 보존

### 컨트리뷰터 의견 작성란
- 텍스트에어리어 (AI 분석에 대한 동의/이의/추가 설명)
- "의견 저장" 버튼

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| AI 분석 요청 | POST /ai-analyze → 분석 결과 표시 |
| 다시 분석 요청 | POST /ai-analyze → 새 분석 결과 (이전 보존) |
| 이전 분석 보기 | GET /ai-analysis?run_seq=N |
| 컨트리뷰터 의견 저장 | PATCH /contributor-comment |

---

## API 연동

### POST /api/v1/pull-requests/{pr_id}/ai-analyze
```
Header: Authorization: Bearer {access_token}

Response 202: (비동기 처리 시)
{
  "analysis_id": 10,
  "status": "processing"
}

또는 Response 200: (동기 처리 시)
{
  "id": 10,
  "run_seq": 1,
  "generated_title": "마법사 아르카의 숨겨진 과거 설정",
  "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
  "structured_content": { ... },
  "contribution_types": ["character_add", "worldbuilding"],
  "score_scope": 8,
  "score_permanence": 7,
  "score_cascade": 9,
  "score_alignment": 6,
  "score_specificity": 7,
  "score_total": 37,
  "ai_grade": "MAJOR",
  "rationale": "...",
  "missing_info": ["캐릭터의 구체적인 나이가 명시되지 않음"],
  "model_name": "gpt-4o-2024-08-06",
  "created_at": "2024-01-01T00:10:00.000000Z"
}
```

### GET /api/v1/pull-requests/{pr_id}/ai-analysis
가장 최근 분석 결과 반환. `?run_seq=N`으로 특정 회차 조회 가능.

### GET /api/v1/pull-requests/{pr_id}/ai-analysis?run_seq=N
특정 회차 분석 결과 반환. 원작자도 동일 엔드포인트 사용.

### PATCH /api/v1/pull-requests/{pr_id}/contributor-comment
```
Header: Authorization: Bearer {access_token}

Request:
{
  "contributor_comment": "AI 분석에서 놓친 부분이 있습니다. 이 캐릭터는..."
}

Response 200:
{
  "pull_request_id": 42,
  "contributor_comment": "..."
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 분석 중 | 로딩 스피너, 버튼 비활성 |
| 분석 결과 없음 | "아직 AI 분석을 요청하지 않았습니다" |
| 분석 실패 | "분석에 실패했습니다. 다시 시도해주세요" |
| 총점 0점 | 내용 부족 경고 메시지 함께 표시 |

---

## 규칙 및 제약

- AI 분석은 컨트리뷰터가 명시적으로 버튼을 눌러야만 호출 (비용 제어)
- `CHANGES_REQUESTED → SUBMITTED` 재제출 시 재분석 허용 (run_seq 증가, 이전 보존)
- 분석 결과는 스냅샷으로 PullRequest.structured_content에도 복사 저장됨
- AI 등급은 참고용이며 원작자가 최종 등급을 조정 가능

---

## 연결 화면

- 결과 확인 후 "제출하기" → 10-pr-submit
- 원작자 PR 상세에서도 동일 패널 표시 (11-pr-detail)
