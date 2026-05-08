# PullRequest 테이블

## 테이블 설명

컨트리뷰터가 작성하는 기여 제안 단위를 저장한다. DRAFT 생성 시점부터 Merge까지의 전체 생애 주기를 단일 테이블에서 관리한다. `first_drafted_at`은 최초 Draft 생성 시 서버 시간으로 1회만 기록되며 이후 절대 갱신하지 않는다.

## 테이블 이름

`pull_requests`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | PR 고유 ID | `42` |
| FK | repository_id | BIGINT | NOT NULL | 대상 Repository. `repositories.id` 참조 | `1` |
| FK | author_id | BIGINT | NOT NULL | PR 작성자(컨트리뷰터). `users.id` 참조 | `2` |
| - | title | VARCHAR(300) | NULL | AI가 생성한 PR 제목. 분석 전이면 NULL | `마법사 아르카의 숨겨진 과거` |
| - | raw_content | LONGTEXT | NULL | 컨트리뷰터가 자유 작성한 원문 | `아르카는 사실...` |
| - | structured_content | JSON | NULL | AI 구조화 결과 스냅샷 | `{"character_name": "아르카"}` |
| - | contribution_types | JSON | NULL | 기여 유형 배열 | `["character_add", "worldbuilding"]` |
| - | visibility | ENUM('PUBLIC', 'PRIVATE') | NOT NULL DEFAULT 'PUBLIC' | 공개 여부 | `PUBLIC` |
| - | status | ENUM('DRAFT', 'SUBMITTED', 'ACCEPTED', 'CHANGES_REQUESTED', 'REJECTED', 'MERGED') | NOT NULL DEFAULT 'DRAFT' | PR 현재 상태 | `SUBMITTED` |
| - | author_grade_override | ENUM('MAJOR', 'NORMAL', 'MINOR') | NULL | 원작자 확정 등급. NULL이면 AI 등급을 최종 등급으로 사용 | `NORMAL` |
| - | author_grade_override_reason | TEXT | NULL | 원작자 등급 조정 사유. AI 등급과 다를 때 필수 | `세계관 영향 범위가 좁습니다.` |
| - | author_review_comment | TEXT | NULL | 수락·거절·병합 시 원작자 코멘트 | `훌륭한 기여입니다.` |
| - | changes_requested_reason | TEXT | NULL | 수정 요청 사유 | `마법 능력이 규칙과 충돌합니다.` |
| - | contributor_comment | TEXT | NULL | AI 분석에 대한 컨트리뷰터 의견 | `AI가 놓친 부분이 있습니다.` |
| - | first_drafted_at | DATETIME(6) | NOT NULL | 최초 Draft 생성 시각. 서버 시간, 절대 갱신 불가 | `2024-01-01 00:00:00.000000` |
| - | last_saved_at | DATETIME(6) | NOT NULL | 마지막 자동저장 시각 | `2024-01-01 00:55:00.000000` |
| - | save_count | INT | NOT NULL DEFAULT 0 | 자동저장 누적 횟수 | `11` |
| - | submitted_at | DATETIME(6) | NULL | 최종 제출 시각. 서버 시간 | `2024-01-01 01:00:00.000000` |
| - | reviewed_at | DATETIME(6) | NULL | 가장 최근 원작자 액션 시각 | `2024-01-02 10:00:00.000000` |
| - | merged_at | DATETIME(6) | NULL | 병합 시각 | `2024-01-03 12:00:00.000000` |
| - | created_at | DATETIME(6) | NOT NULL | 행 생성 시각 (UTC) | `2024-01-01 00:00:00.000000` |
| - | updated_at | DATETIME(6) | NOT NULL | 행 최근 수정 시각 (UTC) | `2024-01-03 12:00:00.000000` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | (repository_id, status, submitted_at DESC) | 원작자가 받은 PR 목록 조회 |
| INDEX | (author_id, status) | 컨트리뷰터 본인 PR 목록 조회 |
| INDEX | submitted_at | 시간순 조회 |

### 상태 전이 규칙

| 현재 상태 | 허용 전이 |
|---|---|
| DRAFT | SUBMITTED |
| SUBMITTED | ACCEPTED, CHANGES_REQUESTED, REJECTED, MERGED |
| ACCEPTED | MERGED |
| CHANGES_REQUESTED | SUBMITTED |
| REJECTED | (없음) |
| MERGED | (없음) |

## Example Row

```json
{
  "id": 42,
  "repository_id": 1,
  "author_id": 2,
  "title": "마법사 아르카의 숨겨진 과거",
  "raw_content": "아르카는 사실 마법사 가문의 후손이 아니라...",
  "structured_content": { "character_name": "아르카", "background": "..." },
  "contribution_types": ["character_add", "worldbuilding"],
  "visibility": "PUBLIC",
  "status": "SUBMITTED",
  "author_grade_override": null,
  "author_grade_override_reason": null,
  "author_review_comment": null,
  "changes_requested_reason": null,
  "contributor_comment": "AI가 놓친 부분이 있습니다. 이 설정은...",
  "first_drafted_at": "2024-01-01 00:00:00.000000",
  "last_saved_at": "2024-01-01 00:55:00.000000",
  "save_count": 11,
  "submitted_at": "2024-01-01 01:00:00.000000",
  "reviewed_at": null,
  "merged_at": null,
  "created_at": "2024-01-01 00:00:00.000000",
  "updated_at": "2024-01-01 01:00:00.000000"
}
```
