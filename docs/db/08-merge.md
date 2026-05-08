# Merge 테이블

## 테이블 설명

원작자가 PR을 공식 작품에 병합한 기록을 저장한다. 하나의 PR에 최대 하나의 Merge가 존재한다. 병합 시 `citation_url`이 발급되며, 이 URL은 외부에서 기여 사실을 인용할 수 있는 영구 퍼머링크다.

## 테이블 이름

`merges`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | Merge 고유 ID | `5` |
| FK | pull_request_id | BIGINT | NOT NULL UNIQUE | 병합된 PR. `pull_requests.id` 참조. UNIQUE — 한 PR에 한 Merge | `42` |
| FK | repository_id | BIGINT | NOT NULL | 대상 Repository. `repositories.id` 참조 | `1` |
| FK | contributor_id | BIGINT | NOT NULL | 기여자. `users.id` 참조 | `2` |
| FK | author_id | BIGINT | NOT NULL | Merge를 수행한 원작자. `users.id` 참조 | `1` |
| - | final_grade | ENUM('MAJOR', 'NORMAL', 'MINOR') | NOT NULL | 최종 기여 등급. 원작자 확정 등급 우선, 없으면 AI 등급 | `MAJOR` |
| - | author_comment | TEXT | NULL | 원작자 코멘트 | `훌륭한 기여입니다.` |
| - | credit_text | VARCHAR(500) | NOT NULL | 작품에 표시될 크레딧 문구 | `아르카의 숨겨진 과거 — 기여: @contributor123` |
| - | readme_apply_note | TEXT | NULL | README에 반영할 내용 (원작자 자유 입력) | `3장 캐릭터 설정에 추가 예정` |
| - | citation_url | VARCHAR(500) | NOT NULL UNIQUE | 외부 인용 가능한 영구 퍼머링크. `/m/{id}` 형태 | `https://worldbuild.example.com/m/5` |
| - | merged_at | DATETIME(6) | NOT NULL | 병합 시각. 서버 시간 | `2024-01-03 12:00:00.000000` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| UNIQUE | pull_request_id | 한 PR에 한 Merge만 허용 |
| UNIQUE | citation_url | 퍼머링크 중복 방지 |
| INDEX | (repository_id, merged_at DESC) | Repository별 Merge 이력 조회 |
| INDEX | (contributor_id, merged_at DESC) | 기여자별 Merge 이력 조회 |

## Example Row

```json
{
  "id": 5,
  "pull_request_id": 42,
  "repository_id": 1,
  "contributor_id": 2,
  "author_id": 1,
  "final_grade": "MAJOR",
  "author_comment": "훌륭한 기여입니다. 공식 설정으로 반영합니다.",
  "credit_text": "아르카의 숨겨진 과거 — 기여: @contributor123",
  "readme_apply_note": "3장 캐릭터 설정에 추가 예정",
  "citation_url": "https://worldbuild.example.com/m/5",
  "merged_at": "2024-01-03 12:00:00.000000"
}
```
