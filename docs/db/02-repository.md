# Repository 테이블

## 테이블 설명

작품·세계관·캐릭터 IP 단위를 저장한다. README 본문(마크다운)과 기여 가이드라인을 포함하며, 캐릭터·지역·규칙 등 자식 컬렉션은 `readme_sections` 테이블에서 관리한다. 태그는 `repository_tags` 조인 테이블로 연결된다.

## 테이블 이름

`repositories`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | Repository 고유 ID | `1` |
| FK | author_id | BIGINT | NOT NULL | 원작자. `users.id` 참조 | `1` |
| - | title | VARCHAR(100) | NOT NULL | 작품 제목 | `내 판타지 세계관` |
| - | description | VARCHAR(500) | NULL | 작품 설명 | `마법이 존재하는 세계의 이야기` |
| - | thumbnail | VARCHAR(500) | NULL | 썸네일 이미지 URL | `https://cdn.example.com/thumb.jpg` |
| - | external_links | JSON | NULL | 외부 링크 목록 (URL 배열, 최대 3개) | `["https://example.com"]` |
| - | readme_content | LONGTEXT | NULL | 작품 설명 마크다운 본문 | `## 세계관 소개\n...` |
| - | contribution_guidelines | LONGTEXT | NULL | 기여 가이드라인 마크다운 | `## 기여 가이드\n...` |
| - | is_active | BOOLEAN | NOT NULL DEFAULT TRUE | 활성 여부. FALSE면 삭제 처리 | `TRUE` |
| - | created_at | DATETIME(6) | NOT NULL | 생성 시각 (UTC) | `2024-01-01 00:00:00.000000` |
| - | updated_at | DATETIME(6) | NOT NULL | 마지막 수정 시각 (UTC) | `2024-06-01 00:00:00.000000` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| INDEX | author_id | 원작자별 Repository 목록 조회 |
| INDEX | created_at DESC | 최신순 정렬 |
| INDEX | (is_active, created_at DESC) | 활성 Repository 목록 조회 |

## Example Row

```json
{
  "id": 1,
  "author_id": 1,
  "title": "내 판타지 세계관",
  "description": "마법이 존재하는 세계의 이야기",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "external_links": ["https://example.com"],
  "readme_content": "## 세계관 소개\n이 세계에는 마법이 존재합니다.",
  "contribution_guidelines": "## 기여 가이드\n세계관을 존중해주세요.",
  "is_active": true,
  "created_at": "2024-01-01 00:00:00.000000",
  "updated_at": "2024-06-01 00:00:00.000000"
}
```
