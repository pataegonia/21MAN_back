# 10 — PR 최종 제출

## 개요

컨트리뷰터가 AI 분석을 확인한 후 PR을 원작자에게 공식 제출하는 페이지. 제출 후 상태가 DRAFT → SUBMITTED로 변경되고, 원작자에게 알림이 전송된다.

---

## 접근 권한

✍️ Draft 소유 컨트리뷰터 본인 (상태가 DRAFT인 경우만)

---

## 화면 구성요소

### 제출 전 최종 확인 영역

#### 요약 카드
- AI 생성 제목
- AI 분석 요약
- 기여 유형 뱃지
- 5축 점수 + 총점
- AI 등급
- 충돌 위험도

#### 원문 미리보기
- `raw_content` 전체 표시 (접이식 가능)

#### 컨트리뷰터 의견 (있는 경우)
- 작성한 의견 표시
- "수정" 버튼 → Draft 작성 페이지로 돌아감

#### 공개 여부 설정
- PUBLIC (기본): 누구나 열람 가능
- PRIVATE: PR 작성자 + 원작자만 열람 가능
- 선택 라디오 버튼 + 설명 안내

### 작성 시점 안내
- 첫 작성 시점 (`first_drafted_at`) 강조 표시
- "이 시각이 아이디어 작성 시작의 공식 증명이 됩니다" 안내 문구

### 제출 버튼
- "최종 제출" (비가역 액션 경고 포함)
- "돌아가서 수정" → Draft 작성 페이지

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 공개 여부 선택 | 로컬 상태 변경 |
| "돌아가서 수정" 클릭 | `/pull-requests/{pr_id}/draft` 이동 |
| "최종 제출" 클릭 | 확인 다이얼로그 → POST /submit → PR 상세로 이동 |

---

## API 연동

### POST /api/v1/pull-requests/{pr_id}/submit
```
Header: Authorization: Bearer {access_token}

Request:
{
  "visibility": "PUBLIC"
}

Response 200:
{
  "pull_request_id": 42,
  "status": "SUBMITTED",
  "submitted_at": "2024-01-01T01:00:00.000000Z",
  "visibility": "PUBLIC"
}
```

**서버 처리 순서:**
1. PR 상태 DRAFT → SUBMITTED 변경
2. `submitted_at` 서버 시간으로 기록
3. 원작자에게 알림 생성 (`PR_SUBMITTED`)
4. AuditLog(`PR_SUBMIT`) 기록
5. 통계 갱신 대상에 포함

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| AI 분석 미완료 | 경고 배너: "AI 분석 없이 제출하면 원작자가 판단하기 어려울 수 있습니다" + 제출 허용(차단 안 함) |
| 이미 SUBMITTED 상태 | "이미 제출된 PR입니다" |
| 제출 실패 | "제출에 실패했습니다. 다시 시도해주세요" |

---

## 규칙 및 제약

- 제출은 비가역 액션: SUBMITTED 후 DRAFT로 되돌릴 수 없음
- `submitted_at`은 서버 시간으로만 기록, 클라이언트 시간 신뢰 안 함
- AI 분석 없이도 제출 가능 (차단 안 함), 단 경고 표시
- DRAFT 상태 PR만 제출 가능 (SUBMITTED/ACCEPTED 등 다른 상태이면 400 반환)
- 제출 후 원작자 알림은 동기 처리 또는 비동기 큐로 처리

---

## 연결 화면

- 제출 성공 → PR 상세 (`/pull-requests/{pr_id}`)
- "돌아가서 수정" → PR Draft 작성 (`/pull-requests/{pr_id}/draft`)
