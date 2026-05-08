# AuditLog 테이블

## 테이블 설명

서비스의 중요한 액션을 영구적으로 기록하는 감사 로그 테이블이다. PR 제출·열람·수락·수정요청·거절·병합·등급조정·Repository 수정 시 반드시 행이 INSERT된다. 분쟁 방지와 감사 추적을 위해 UPDATE와 DELETE를 절대 수행하지 않는다.

## 테이블 이름

`audit_logs`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | AuditLog 고유 ID | `1` |
| FK | actor_id | BIGINT | NULL | 액션을 수행한 사용자. `users.id` 참조. 시스템 액션이면 NULL | `1` |
| - | action_type | VARCHAR(50) | NOT NULL | 액션 유형. 아래 값 목록 참조 | `PR_SUBMIT` |
| - | target_type | VARCHAR(50) | NOT NULL | 액션 대상 타입 (`pull_request`, `repository`) | `pull_request` |
| - | target_id | BIGINT | NOT NULL | 액션 대상 행의 ID | `42` |
| - | payload | JSON | NULL | 액션별 추가 상세 정보 (전후 등급, 사유 등) | `{"from_grade": "MAJOR", "to_grade": "NORMAL"}` |
| - | created_at | DATETIME(6) | NOT NULL | 기록 시각. 서버 시간 | `2024-01-02 10:00:00.000000` |

### action_type 값 목록

| 값 | 설명 | target_type |
|---|---|---|
| `PR_SUBMIT` | PR 최종 제출 | `pull_request` |
| `PR_VIEW` | 원작자가 PR 열람 | `pull_request` |
| `PR_ACCEPT` | 원작자가 PR 수락 | `pull_request` |
| `PR_REQUEST_CHANGES` | 원작자가 수정 요청 | `pull_request` |
| `PR_REJECT` | 원작자가 PR 거절 | `pull_request` |
| `PR_MERGE` | 원작자가 PR 병합 | `pull_request` |
| `PR_GRADE_OVERRIDE` | 원작자가 등급 조정 | `pull_request` |
| `REPO_UPDATE` | Repository 주요 정보 수정 | `repository` |

### 무결성 규칙

- **INSERT 전용**: UPDATE, DELETE는 서비스 레이어에서 절대 호출하지 않는다.
- 각 액션 발생 시 동기 처리로 즉시 INSERT한다.

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | (target_type, target_id, created_at) | 대상별 감사 이력 조회 |
| INDEX | (actor_id, created_at) | 행위자별 감사 이력 조회 |
| INDEX | (action_type, created_at) | 액션 유형별 조회 |

## Example Row

```json
[
  {
    "id": 1,
    "actor_id": 2,
    "action_type": "PR_SUBMIT",
    "target_type": "pull_request",
    "target_id": 42,
    "payload": {
      "visibility": "PUBLIC"
    },
    "created_at": "2024-01-01 01:00:00.000000"
  },
  {
    "id": 2,
    "actor_id": 1,
    "action_type": "PR_VIEW",
    "target_type": "pull_request",
    "target_id": 42,
    "payload": null,
    "created_at": "2024-01-02 10:00:00.000000"
  },
  {
    "id": 3,
    "actor_id": 1,
    "action_type": "PR_GRADE_OVERRIDE",
    "target_type": "pull_request",
    "target_id": 42,
    "payload": {
      "from_grade": "MAJOR",
      "to_grade": "NORMAL",
      "reason": "세계관 영향 범위가 생각보다 작습니다."
    },
    "created_at": "2024-01-02 11:00:00.000000"
  },
  {
    "id": 4,
    "actor_id": 1,
    "action_type": "PR_MERGE",
    "target_type": "pull_request",
    "target_id": 42,
    "payload": {
      "final_grade": "NORMAL",
      "merge_id": 5
    },
    "created_at": "2024-01-03 12:00:00.000000"
  }
]
```
