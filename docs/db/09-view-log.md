# ViewLog 테이블

## 테이블 설명

원작자가 PR을 열람한 기록을 저장한다. 기여자의 아이디어가 원작자에게 실제로 노출되었는지를 증명하기 위한 핵심 무결성 테이블이다. 한 PR을 여러 번 열람하면 매번 새 행이 INSERT된다. 서비스 레이어에서 이 테이블에 대한 UPDATE와 DELETE를 절대 호출하지 않는다.

## 테이블 이름

`view_logs`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | ViewLog 고유 ID | `1` |
| FK | pull_request_id | BIGINT | NOT NULL | 열람된 PR. `pull_requests.id` 참조 | `42` |
| FK | viewer_id | BIGINT | NOT NULL | 열람자. 원작자만 기록. `users.id` 참조 | `1` |
| - | viewed_at | DATETIME(6) | NOT NULL | 열람 시각. 서버 시간 | `2024-01-02 10:00:00.000000` |
| - | ip_hash | CHAR(64) | NULL | SHA-256(IP + secret). 원본 IP는 저장하지 않음 | `a3f8c2...` |
| - | day_bucket_hash | CHAR(64) | NULL | SHA-256(viewer_id + YYYYMMDD + secret). 같은 날 중복 열람 분석용 | `9b7d1e...` |

### 무결성 규칙

- **INSERT 전용**: UPDATE, DELETE는 서비스 레이어에서 절대 호출하지 않는다.
- **기록 조건**: viewer가 해당 Repository의 원작자이고, PR 작성자 본인이 아닐 때만 INSERT한다.
- **중복 허용**: 같은 PR을 여러 번 열람하면 매번 별도 행이 생성된다.

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | (pull_request_id, viewed_at) | PR별 열람 이력 조회 |
| INDEX | (viewer_id, viewed_at) | 원작자별 열람 이력 조회 |

## Example Row

```json
[
  {
    "id": 1,
    "pull_request_id": 42,
    "viewer_id": 1,
    "viewed_at": "2024-01-02 10:00:00.000000",
    "ip_hash": "a3f8c2d1e4b5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
    "day_bucket_hash": "9b7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d"
  },
  {
    "id": 2,
    "pull_request_id": 42,
    "viewer_id": 1,
    "viewed_at": "2024-01-02 14:30:00.000000",
    "ip_hash": "a3f8c2d1e4b5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
    "day_bucket_hash": "9b7d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d"
  }
]
```
