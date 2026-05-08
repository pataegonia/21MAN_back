# RejectReason 테이블

## 테이블 설명

원작자가 PR을 거절한 사유를 저장한다. 사유는 영구 보존되며 DELETE하지 않는다. 사유를 변경할 때는 기존 행에 `superseded_by_id`를 채우고 새 행을 INSERT한다(체인 방식). 현재 유효한 사유는 `superseded_by_id IS NULL`인 행이다.

## 테이블 이름

`reject_reasons`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | RejectReason 고유 ID | `1` |
| FK | pull_request_id | BIGINT | NOT NULL | 거절된 PR. `pull_requests.id` 참조 | `42` |
| - | category | ENUM('CONFLICT', 'TOO_VAGUE', 'OUT_OF_SCOPE', 'MISALIGNED', 'DUPLICATE', 'INAPPROPRIATE', 'OTHER') | NOT NULL | 거절 카테고리 | `CONFLICT` |
| - | detail | TEXT | NOT NULL | 거절 상세 사유 | `이 설정은 기존 마법 금지 설정과 충돌합니다.` |
| FK | created_by | BIGINT | NOT NULL | 사유를 등록한 원작자. `users.id` 참조 | `1` |
| - | created_at | DATETIME(6) | NOT NULL | 등록 시각. 서버 시간 | `2024-01-02 10:00:00.000000` |
| FK | superseded_by_id | BIGINT | NULL | 이 행을 대체한 새 RejectReason의 ID. 현재 유효한 행이면 NULL | `null` |
| - | superseded_at | DATETIME(6) | NULL | 이 행이 대체된 시각. NULL이면 현재 유효한 행 | `null` |

### category 값 목록

| 값 | 설명 |
|---|---|
| `CONFLICT` | 기존 세계관과 충돌 |
| `TOO_VAGUE` | 기여 내용이 너무 모호함 |
| `OUT_OF_SCOPE` | 모집 영역과 맞지 않음 |
| `MISALIGNED` | 원작 방향성과 맞지 않음 |
| `DUPLICATE` | 이미 존재하는 설정과 중복 |
| `INAPPROPRIATE` | 부적절한 내용 |
| `OTHER` | 기타 |

### 무결성 규칙

- **DELETE 금지**: 사유는 삭제하지 않는다.
- **수정 방법**: 기존 행의 `superseded_by_id`에 새 행 ID를 기록하고, `superseded_at`에 대체 시각을 기록한다. 새 행을 INSERT한다.
- **현재 유효 사유 조회**: `WHERE pull_request_id = ? AND superseded_by_id IS NULL`

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | pull_request_id | PR별 거절 사유 조회 |
| INDEX | (pull_request_id, superseded_by_id) | 현재 유효한 사유 조회 |

## Example Row

사유 변경 이력 예시 (id=1이 id=2로 대체된 경우):

```json
[
  {
    "id": 1,
    "pull_request_id": 42,
    "category": "CONFLICT",
    "detail": "이 설정은 기존 세계관의 마법 금지 설정과 충돌합니다.",
    "created_by": 1,
    "created_at": "2024-01-02 10:00:00.000000",
    "superseded_by_id": 2,
    "superseded_at": "2024-01-03 09:00:00.000000"
  },
  {
    "id": 2,
    "pull_request_id": 42,
    "category": "MISALIGNED",
    "detail": "재검토 결과, 원작 방향성과 맞지 않는 점이 더 큰 이유입니다.",
    "created_by": 1,
    "created_at": "2024-01-03 09:00:00.000000",
    "superseded_by_id": null,
    "superseded_at": null
  }
]
```
