# AiAnalysis 테이블

## 테이블 설명

PR에 대한 AI 분석 결과를 저장한다. 같은 PR에 대해 여러 번 분석을 요청할 수 있으며, 각 분석은 `run_seq`로 구분된다. 이전 분석 결과는 삭제하지 않고 영구 보존한다. `CHANGES_REQUESTED → SUBMITTED` 재제출 후 재분석 시 `run_seq`가 증가한다.

## 테이블 이름

`ai_analyses`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | AiAnalysis 고유 ID | `10` |
| FK | pull_request_id | BIGINT | NOT NULL | 분석 대상 PR. `pull_requests.id` 참조 | `42` |
| - | run_seq | INT | NOT NULL | 같은 PR 내 분석 회차. 1부터 시작 | `1` |
| - | generated_title | VARCHAR(300) | NULL | AI가 생성한 PR 제목 | `마법사 아르카의 숨겨진 과거 설정` |
| - | summary | TEXT | NULL | AI가 생성한 내용 요약 | `주인공의 출생 비밀을 통해...` |
| - | structured_content | JSON | NULL | AI가 구조화한 PR 내용 | `{"character_name": "아르카"}` |
| - | contribution_types | JSON | NULL | AI가 분류한 기여 유형 배열 | `["character_add", "worldbuilding"]` |
| - | score_scope | TINYINT | NULL | Scope 점수 (0~10). 작품 영향 범위 | `8` |
| - | score_permanence | TINYINT | NULL | Permanence 점수 (0~10). 설정의 장기 지속성 | `7` |
| - | score_cascade | TINYINT | NULL | Cascade 점수 (0~10). 다른 설정에 연쇄 영향 | `9` |
| - | score_alignment | TINYINT | NULL | Alignment 점수 (0~10). 기존 세계관과의 정합성 | `6` |
| - | score_specificity | TINYINT | NULL | Specificity 점수 (0~10). 제안의 구체성 | `7` |
| - | score_total | TINYINT | NULL | 5축 합산 총점 (0~50) | `37` |
| - | ai_grade | ENUM('MAJOR', 'NORMAL', 'MINOR') | NULL | AI 판정 등급. MAJOR≥25, NORMAL 12~24, MINOR<12 | `MAJOR` |
| - | rationale | TEXT | NULL | 평가 근거 및 분석 설명 | `캐릭터의 출생 비밀은...` |
| - | missing_info | JSON | NULL | AI가 파악한 누락 정보 목록 | `["구체적인 나이가 명시되지 않음"]` |
| - | model_name | VARCHAR(100) | NULL | 사용된 AI 모델 식별자 | `gpt-4o-2024-08-06` |
| - | created_at | DATETIME(6) | NOT NULL | 분석 생성 시각 (UTC) | `2024-01-01 00:10:00.000000` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| UNIQUE | (pull_request_id, run_seq) | 같은 PR 내 회차 중복 방지 |
| INDEX | (pull_request_id, created_at DESC) | 최근 분석 결과 조회 |

## Example Row

```json
{
  "id": 10,
  "pull_request_id": 42,
  "run_seq": 1,
  "generated_title": "마법사 아르카의 숨겨진 과거 설정",
  "summary": "주인공의 출생 비밀을 통해 세계관 갈등 구조를 강화하는 제안",
  "structured_content": {
    "character_name": "아르카",
    "background": "귀족 가문의 사생아로 태어났으나 진실은..."
  },
  "contribution_types": ["character_add", "worldbuilding"],
  "score_scope": 8,
  "score_permanence": 7,
  "score_cascade": 9,
  "score_alignment": 6,
  "score_specificity": 7,
  "score_total": 37,
  "ai_grade": "MAJOR",
  "rationale": "캐릭터의 출생 비밀은 세계관 전체에 영향을 미치며 기존 규칙과 조화를 이룹니다.",
  "missing_info": ["캐릭터의 구체적인 나이가 명시되지 않음"],
  "model_name": "gpt-4o-2024-08-06",
  "created_at": "2024-01-01 00:10:00.000000"
}
```
