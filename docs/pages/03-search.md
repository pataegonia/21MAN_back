# 03 — 통합 검색

## 개요

Repository와 User를 통합 검색하는 페이지. 키워드, 태그, 모집 영역, 정렬 기준으로 필터링할 수 있다.

---

## 접근 권한

🌐 누구나

---

## 화면 구성요소

### 검색 입력부
- 검색창 (URL 파라미터 `q`와 동기화)
- 검색 타입 탭: 전체 / Repository / 사용자
- 정렬 옵션: 최신순 / 인기순

### Repository 필터 사이드바 (Repository 탭 활성 시)
- 태그 멀티 선택
- 모집 영역 필터 (캐릭터 추가, 세계관 설정 등)
- 인기 태그 퀵 선택

### 검색 결과 영역
- Repository 카드 목록 (썸네일, 제목, 원작자, 태그, Merge 수)
- User 카드 목록 (아바타, username, bio, Merge 수)
- 결과 수 표시 ("총 {n}개")
- 페이지네이션

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 키워드 변경 | URL `q` 파라미터 갱신, 결과 재조회 |
| 탭 전환 | `type` 파라미터 변경 |
| 정렬 변경 | `sort` 파라미터 변경 |
| 태그 선택/해제 | `tag` 파라미터 추가/제거 |
| Repository 카드 클릭 | `/repositories/{repo_id}` 이동 |
| User 카드 클릭 | `/users/{username}` 이동 |

---

## API 연동

### GET /api/v1/search
```
Query params:
  q       - 검색 키워드 (제목, 설명, username에 LIKE 검색)
  type    - repository | user | all (기본: all)
  sort    - latest | popular (기본: latest)
  tag     - 태그명 (반복 가능: ?tag=판타지&tag=SF)
  page    - 페이지 번호 (기본: 1)
  size    - 페이지 크기 (기본: 20, 최대: 100)

Response 200:
{
  "repositories": {
    "items": [
      {
        "id": 1,
        "title": "...",
        "description": "...",
        "thumbnail": "...",
        "tags": ["..."],
        "author": { "username": "...", "avatar": "..." },
        "merge_count": 5
      }
    ],
    "total": 50
  },
  "users": {
    "items": [
      {
        "username": "...",
        "avatar": "...",
        "bio": "...",
        "merge_count": 3
      }
    ],
    "total": 10
  }
}
```

### GET /api/v1/tags?q={keyword}
태그 자동완성용.
```
Response 200:
{
  "tags": [
    { "id": 1, "name": "판타지" }
  ]
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 검색어 없음 | 전체 목록 표시 (sort=latest) |
| 검색 결과 없음 | "검색 결과가 없습니다. 다른 키워드를 시도해보세요" |
| 로딩 중 | 스켈레톤 UI |

---

## 규칙 및 제약

- MVP에서는 LIKE 검색 사용, 데이터 증가 후 FULLTEXT로 교체 예정
- `q` 파라미터가 없으면 빈 검색으로 처리하고 전체 결과 반환
- 태그 필터는 Repository 검색에만 적용
- URL 파라미터로 검색 상태를 관리 (공유 가능한 URL)

---

## 연결 화면

- → Repository 상세 (`/repositories/{repo_id}`)
- → 사용자 프로필 (`/users/{username}`)
