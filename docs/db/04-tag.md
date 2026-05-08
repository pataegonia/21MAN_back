# Tag / RepositoryTag 테이블

## 테이블 설명

`tags`: 서비스 전역에서 사용하는 태그를 저장한다. 태그 이름은 UNIQUE하며 한 번 등록된 태그는 재활용된다.

`repository_tags`: Repository와 Tag 간의 다대다 관계를 연결하는 조인 테이블이다.

---

## tags

### 테이블 이름

`tags`

### 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | 태그 고유 ID | `1` |
| - | name | VARCHAR(50) | NOT NULL UNIQUE | 태그 이름 | `판타지` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| UNIQUE | name | 태그 이름 중복 방지 |

### Example Row

```json
[
  { "id": 1, "name": "판타지" },
  { "id": 2, "name": "SF" },
  { "id": 3, "name": "마법" }
]
```

---

## repository_tags

### 테이블 이름

`repository_tags`

### 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK, FK | repository_id | BIGINT | NOT NULL | 복합 PK 구성 요소. `repositories.id` 참조 | `1` |
| PK, FK | tag_id | BIGINT | NOT NULL | 복합 PK 구성 요소. `tags.id` 참조 | `1` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| PK | (repository_id, tag_id) | 복합 기본 키 |
| INDEX | tag_id | 태그로 Repository를 역방향 조회 |

### Example Row

```json
[
  { "repository_id": 1, "tag_id": 1 },
  { "repository_id": 1, "tag_id": 3 }
]
```
