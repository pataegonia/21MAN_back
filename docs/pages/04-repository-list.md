# 04 — Repository 목록

## 개요

등록된 모든 Repository를 탐색하는 전용 목록 페이지. 검색·필터·정렬을 지원한다.

---

## 접근 권한

🌐 누구나

---

## 화면 구성요소

### 필터 / 정렬 영역
- 검색창 (키워드)
- 태그 필터 (멀티 선택)
- 모집 영역 필터
- 정렬: 최신순 / 인기순

### Repository 카드 목록
- 썸네일
- 제목
- 원작자 (아바타 + username)
- 태그 (최대 3개 + 더보기)
- 설명 요약 (2줄 말줄임)
- Merge 수 / PR 수
- 생성일 또는 최근 활동일

### 페이지네이션
- 이전/다음 페이지 버튼
- 현재 페이지 / 전체 페이지 표시

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 키워드 입력 | 제목·설명·원작자 username으로 필터링 |
| 태그 선택 | 해당 태그를 가진 Repository만 표시 |
| 모집 영역 선택 | 해당 모집 영역이 활성화된 Repository만 표시 |
| 정렬 변경 | 결과 재정렬 |
| Repository 카드 클릭 | `/repositories/{repo_id}` 이동 |
| "새 Repository 만들기" 버튼 | `/repositories/new` 이동 (로그인 필요) |

---

## API 연동

### GET /api/v1/repositories
```
Query params:
  q           - 키워드 검색
  tag         - 태그 (반복 가능)
  recruiting  - 모집 영역 (예: character_add)
  sort        - latest | popular (기본: latest)
  page        - 페이지 번호 (기본: 1)
  size        - 페이지 크기 (기본: 20, 최대: 100)

Response 200:
{
  "items": [
    {
      "id": 1,
      "title": "...",
      "description": "...",
      "thumbnail": "...",
      "tags": ["판타지", "SF"],
      "author": {
        "id": 1,
        "username": "...",
        "avatar": "..."
      },
      "merge_count": 5,
      "pr_count": 12,
      "recruiting_areas": ["character_add", "worldbuilding"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-06-01T00:00:00Z"
    }
  ],
  "total": 200,
  "page": 1,
  "size": 20
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 목록 없음 | "아직 등록된 작품이 없습니다" |
| 필터 결과 없음 | "조건에 맞는 작품이 없습니다. 필터를 변경해보세요" |
| 로딩 중 | 카드 스켈레톤 UI |

---

## 규칙 및 제약

- URL 파라미터로 필터 상태 관리 (공유 가능)
- 태그와 모집 영역 필터는 AND 조건으로 적용
- 썸네일 없는 경우 기본 이미지 표시

---

## 연결 화면

- → Repository 상세 (`/repositories/{repo_id}`)
- → Repository 생성 (`/repositories/new`)
