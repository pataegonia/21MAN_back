# Notification 테이블

## 테이블 설명

사용자에게 전달할 인앱 알림을 저장한다. 알림은 주요 이벤트 발생 시 서버에서 자동으로 생성한다. 읽음 처리는 `is_read`와 `read_at`으로 관리한다.

## 테이블 이름

`notifications`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | 알림 고유 ID | `10` |
| FK | recipient_id | BIGINT | NOT NULL | 알림 수신자. `users.id` 참조 | `2` |
| - | type | VARCHAR(50) | NOT NULL | 알림 유형. 아래 값 목록 참조 | `PR_MERGED` |
| - | payload | JSON | NULL | 알림 상세 데이터 (pr_id, repo_id, actor_id 등) | `{"pr_id": 42, ...}` |
| - | is_read | BOOLEAN | NOT NULL DEFAULT FALSE | 읽음 여부 | `FALSE` |
| - | created_at | DATETIME(6) | NOT NULL | 알림 생성 시각 (UTC) | `2024-01-03 12:00:00.000000` |
| - | read_at | DATETIME(6) | NULL | 읽음 처리 시각. 미읽음이면 NULL | `null` |

### type 값 목록

| 값 | 수신자 | 발생 시점 |
|---|---|---|
| `PR_SUBMITTED` | 원작자 | 컨트리뷰터가 PR 제출 |
| `PR_RESUBMITTED` | 원작자 | CHANGES_REQUESTED → SUBMITTED 재제출 |
| `PR_COMMENT_ADDED` | 원작자 | 컨트리뷰터 의견 추가 |
| `PR_ACCEPTED` | 컨트리뷰터 | 원작자가 수락 |
| `PR_CHANGES_REQUESTED` | 컨트리뷰터 | 원작자가 수정 요청 |
| `PR_REJECTED` | 컨트리뷰터 | 원작자가 거절 |
| `PR_MERGED` | 컨트리뷰터 | 원작자가 병합 |
| `GRADE_ADJUSTED` | 컨트리뷰터 | 원작자가 등급 조정 |

### payload 구조 예시

| type | payload 필드 |
|---|---|
| `PR_SUBMITTED` | `pr_id`, `repo_id`, `repo_title`, `actor_id`, `actor_username` |
| `PR_MERGED` | `pr_id`, `pr_title`, `repo_id`, `repo_title`, `actor_id`, `actor_username`, `final_grade` |
| `GRADE_ADJUSTED` | `pr_id`, `pr_title`, `actor_id`, `actor_username`, `new_grade` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | (recipient_id, is_read, created_at DESC) | 수신자별 미읽음 알림 목록 조회 |
| INDEX | (recipient_id, created_at DESC) | 수신자별 전체 알림 목록 조회 |

## Example Row

```json
[
  {
    "id": 10,
    "recipient_id": 2,
    "type": "PR_MERGED",
    "payload": {
      "pr_id": 42,
      "pr_title": "마법사 아르카의 숨겨진 과거",
      "repo_id": 1,
      "repo_title": "내 판타지 세계관",
      "actor_id": 1,
      "actor_username": "creator123",
      "final_grade": "MAJOR"
    },
    "is_read": false,
    "created_at": "2024-01-03 12:00:00.000000",
    "read_at": null
  },
  {
    "id": 11,
    "recipient_id": 2,
    "type": "GRADE_ADJUSTED",
    "payload": {
      "pr_id": 42,
      "pr_title": "마법사 아르카의 숨겨진 과거",
      "actor_id": 1,
      "actor_username": "creator123",
      "new_grade": "NORMAL"
    },
    "is_read": true,
    "created_at": "2024-01-02 11:00:00.000000",
    "read_at": "2024-01-02 11:30:00.000000"
  }
]
```
