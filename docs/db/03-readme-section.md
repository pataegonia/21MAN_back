# ReadmeSection 테이블

## 테이블 설명

Repository의 README를 구성하는 자식 항목(캐릭터, 지역, 세계관 규칙, 금지 설정, 모집 영역)을 저장한다. `section_type`으로 종류를 구분하는 단일 테이블 구조를 사용한다. `PATCH /repositories/{repo_id}` 요청 시 기존 행을 소프트 삭제(`is_active = FALSE`)하고 새 행을 INSERT하는 방식으로 전체 배열을 교체한다.

## 테이블 이름

`readme_sections`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | 항목 고유 ID | `1` |
| FK | repository_id | BIGINT | NOT NULL | 소속 Repository. `repositories.id` 참조 | `1` |
| - | section_type | ENUM('CHARACTER', 'REGION', 'WORLD_RULE', 'FORBIDDEN', 'RECRUITING') | NOT NULL | 항목 종류 | `CHARACTER` |
| - | name | VARCHAR(100) | NULL | 항목 이름. CHARACTER·REGION·RECRUITING에서 사용 | `아르카` |
| - | content | TEXT | NULL | 항목 설명 또는 규칙 본문. WORLD_RULE·FORBIDDEN은 content만 사용 | `주인공 마법사` |
| - | sort_order | INT | NOT NULL DEFAULT 0 | 동일 type 내 표시 순서 | `0` |
| - | is_active | BOOLEAN | NOT NULL DEFAULT TRUE | 활성 여부. FALSE면 수정으로 인해 대체된 항목 | `TRUE` |
| - | created_at | DATETIME(6) | NOT NULL | 생성 시각 (UTC) | `2024-01-01 00:00:00.000000` |
| - | updated_at | DATETIME(6) | NOT NULL | 마지막 수정 시각 (UTC) | `2024-01-01 00:00:00.000000` |

### section_type별 컬럼 사용 규칙

| section_type | name | content |
|---|---|---|
| CHARACTER | 캐릭터 이름 | 캐릭터 설명 |
| REGION | 지역 이름 | 지역 설명 |
| WORLD_RULE | NULL | 규칙 본문 |
| FORBIDDEN | NULL | 금지 설정 본문 |
| RECRUITING | 모집 영역 코드 (예: `character_add`) | NULL |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | (repository_id, section_type, is_active) | Repository별 타입별 활성 항목 조회 |
| INDEX | (repository_id, sort_order) | 정렬 순서 조회 |

## Example Row

```json
[
  {
    "id": 1,
    "repository_id": 1,
    "section_type": "CHARACTER",
    "name": "아르카",
    "content": "주인공 마법사. 귀족 가문 출신이지만 출생의 비밀을 숨기고 있다.",
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01 00:00:00.000000",
    "updated_at": "2024-01-01 00:00:00.000000"
  },
  {
    "id": 2,
    "repository_id": 1,
    "section_type": "REGION",
    "name": "에테르 왕국",
    "content": "마법이 가장 발달한 나라. 마법사 귀족이 지배한다.",
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01 00:00:00.000000",
    "updated_at": "2024-01-01 00:00:00.000000"
  },
  {
    "id": 3,
    "repository_id": 1,
    "section_type": "WORLD_RULE",
    "name": null,
    "content": "마법은 감정에 반응한다.",
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01 00:00:00.000000",
    "updated_at": "2024-01-01 00:00:00.000000"
  },
  {
    "id": 4,
    "repository_id": 1,
    "section_type": "FORBIDDEN",
    "name": null,
    "content": "신이 직접 등장하는 설정",
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01 00:00:00.000000",
    "updated_at": "2024-01-01 00:00:00.000000"
  },
  {
    "id": 5,
    "repository_id": 1,
    "section_type": "RECRUITING",
    "name": "character_add",
    "content": null,
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-01 00:00:00.000000",
    "updated_at": "2024-01-01 00:00:00.000000"
  }
]
```
