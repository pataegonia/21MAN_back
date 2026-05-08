# ConflictCheck 테이블

## 테이블 설명

AI 분석 시 수행한 세계관 충돌 검사 결과를 항목별로 저장한다. 하나의 `ai_analyses` 행에 여러 검사 항목이 연결된다. AI 분석 결과의 일부로 생성되며, 분석이 보존되는 한 함께 보존된다.

## 테이블 이름

`conflict_checks`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | ConflictCheck 고유 ID | `1` |
| FK | ai_analysis_id | BIGINT | NOT NULL | 소속 AI 분석. `ai_analyses.id` 참조 | `10` |
| - | risk_level | ENUM('LOW', 'MEDIUM', 'HIGH') | NOT NULL | 충돌 위험도 | `LOW` |
| - | check_target | VARCHAR(50) | NOT NULL | 검사 대상 항목 (`readme`, `character`, `region`, `world_rule`, `forbidden`, `recent_merge`, `similar_pr`) | `readme` |
| - | target_ref_id | BIGINT | NULL | 충돌이 감지된 대상 행의 ID. 해당되는 경우만 기록 | `null` |
| - | passed | BOOLEAN | NOT NULL | 검사 통과 여부 | `TRUE` |
| - | detail | TEXT | NOT NULL | 검사 결과 상세 설명 | `기존 README와 충돌 없음` |
| - | missing_info | TEXT | NULL | 판단에 필요한 누락 정보 | `null` |
| - | created_at | DATETIME(6) | NOT NULL | 생성 시각 (UTC) | `2024-01-01 00:10:00.000000` |

### check_target 값 목록

| 값 | 설명 |
|---|---|
| `readme` | Repository README 본문과의 충돌 |
| `character` | 기존 캐릭터 설정과의 충돌 |
| `region` | 기존 지역 설정과의 충돌 |
| `world_rule` | 핵심 세계관 규칙과의 충돌 |
| `forbidden` | 금지 설정 위반 |
| `recent_merge` | 최근 Merge된 PR과의 충돌 |
| `similar_pr` | 유사한 기존 PR 존재 여부 |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | ai_analysis_id | 분석별 검사 결과 조회 |

## Example Row

```json
[
  {
    "id": 1,
    "ai_analysis_id": 10,
    "risk_level": "LOW",
    "check_target": "readme",
    "target_ref_id": null,
    "passed": true,
    "detail": "기존 README와 충돌 없음",
    "missing_info": null,
    "created_at": "2024-01-01 00:10:00.000000"
  },
  {
    "id": 2,
    "ai_analysis_id": 10,
    "risk_level": "LOW",
    "check_target": "forbidden",
    "target_ref_id": null,
    "passed": true,
    "detail": "금지 설정에 해당하지 않음",
    "missing_info": null,
    "created_at": "2024-01-01 00:10:00.000000"
  },
  {
    "id": 3,
    "ai_analysis_id": 10,
    "risk_level": "MEDIUM",
    "check_target": "world_rule",
    "target_ref_id": 3,
    "passed": false,
    "detail": "제안된 마법 능력이 '마법은 감정에 반응한다' 규칙과 일부 충돌 가능성이 있습니다.",
    "missing_info": "캐릭터의 능력 발현 조건이 명시되지 않음",
    "created_at": "2024-01-01 00:10:00.000000"
  }
]
```
