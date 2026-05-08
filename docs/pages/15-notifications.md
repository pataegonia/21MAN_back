# 15 — 알림

## 개요

사용자에게 발생한 주요 이벤트 알림을 인앱으로 제공하는 페이지. 헤더의 알림 아이콘과 알림 전체 목록 페이지로 구성된다.

---

## 접근 권한

🔑 로그인 사용자 본인

---

## 화면 구성요소

### 헤더 알림 아이콘 (글로벌)
- 알림 아이콘 + 읽지 않은 수 뱃지
- 클릭 시 알림 드롭다운 (최근 5~10개) 또는 알림 페이지 이동

### 알림 목록 페이지 (/notifications)
- "읽지 않은 알림만 보기" 토글
- "전체 읽음" 버튼
- 알림 항목 목록

### 알림 항목
- 알림 유형 아이콘
- 알림 메시지 텍스트
- 관련 Repository / PR 링크
- 발생 시각 (상대 시간: "3분 전", "2일 전")
- 읽음 상태 (미읽음: 강조 표시)
- 클릭 시 읽음 처리 + 관련 페이지 이동

---

## 알림 유형별 메시지

| 유형 | 수신자 | 메시지 예시 |
|------|--------|-------------|
| `PR_SUBMITTED` | 원작자 | "@contributor_name 님이 [작품명]에 새 기여를 제안했습니다." |
| `PR_RESUBMITTED` | 원작자 | "@contributor_name 님이 수정 요청에 따라 PR을 재제출했습니다." |
| `PR_COMMENT_ADDED` | 원작자 | "@contributor_name 님이 PR에 의견을 추가했습니다." |
| `PR_ACCEPTED` | 컨트리뷰터 | "[원작자명] 님이 내 PR을 수락했습니다." |
| `PR_CHANGES_REQUESTED` | 컨트리뷰터 | "[원작자명] 님이 수정을 요청했습니다." |
| `PR_REJECTED` | 컨트리뷰터 | "[원작자명] 님이 내 PR을 거절했습니다." |
| `PR_MERGED` | 컨트리뷰터 | "[원작자명] 님이 내 기여를 공식 설정에 반영했습니다!" |
| `GRADE_ADJUSTED` | 컨트리뷰터 | "[원작자명] 님이 기여 등급을 [MAJOR]로 조정했습니다." |

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 알림 항목 클릭 | 읽음 처리 → 관련 페이지 이동 |
| "전체 읽음" 버튼 | 모든 알림 읽음 처리 |
| "읽지 않은 것만" 토글 | 미읽음 알림만 필터링 |

---

## API 연동

### GET /api/v1/notifications/unread-count
헤더 뱃지 카운터용. 폴링 또는 WebSocket 연결 시 사용.
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "count": 3
}
```

### GET /api/v1/notifications?unread_only=false&page=1&size=20
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "items": [
    {
      "id": 10,
      "type": "PR_MERGED",
      "payload": {
        "pr_id": 42,
        "pr_title": "마법사 아르카의 과거",
        "repo_id": 1,
        "repo_title": "내 판타지 세계관",
        "actor_id": 5,
        "actor_username": "author123"
      },
      "is_read": false,
      "created_at": "2024-01-03T12:00:00Z",
      "read_at": null
    }
  ],
  "total": 15,
  "unread_count": 3
}
```

### POST /api/v1/notifications/{id}/read
단건 읽음 처리.
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "id": 10,
  "is_read": true,
  "read_at": "2024-01-04T09:00:00Z"
}
```

### POST /api/v1/notifications/read-all
전체 읽음 처리.
```
Header: Authorization: Bearer {access_token}

Response 200:
{
  "updated_count": 3
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 알림 없음 | "아직 알림이 없습니다" |
| 읽지 않은 알림 없음 | "모든 알림을 읽었습니다" |

---

## 규칙 및 제약

- MVP 알림 방식: 인앱 알림 필수, 이메일/푸시는 후순위
- 알림은 본인 알림만 조회 가능 (다른 사용자의 알림 조회 불가)
- 알림 생성 시점: 각 서버 액션이 완료된 직후
- 알림 정렬: 생성일 내림차순 (최신 우선)
- 읽지 않은 수는 `/unread-count`로 별도 조회 (목록 API 매번 호출 방지)

---

## 연결 화면

- → PR 상세 (`/pull-requests/{pr_id}`)
- → Repository 상세 (`/repositories/{repo_id}`)
