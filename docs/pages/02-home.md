# 02 — 홈 / 랜딩

## 개요

서비스 진입점. 인기 Repository와 최신 Repository를 노출해 탐색을 유도하고, 검색창을 제공한다.

---

## 접근 권한

🌐 누구나

---

## 화면 구성요소

### 헤더
- 서비스 로고
- 검색창 (엔터 또는 아이콘 클릭 시 `/search?q=...`로 이동)
- 로그인 / 회원가입 버튼 (비로그인)
- 내 프로필 아바타 + 알림 아이콘 (로그인)

### 인기 Repository 섹션
- 카드 목록 (최대 6~12개)
- 카드 구성: 썸네일, 제목, 원작자, 태그, Merge 수

### 최신 Repository 섹션
- 카드 목록 (최대 6~12개)
- 카드 구성: 썸네일, 제목, 원작자, 태그, 생성일

### 인기 태그 섹션
- 태그 칩 목록 (클릭 시 `/search?tag=...`)

### CTA (Call To Action)
- 비로그인 사용자: "내 세계관 등록하기" 버튼 → 로그인 페이지
- 로그인 사용자: "Repository 만들기" 버튼 → `/repositories/new`

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| Repository 카드 클릭 | `/repositories/{repo_id}` 이동 |
| 검색창 입력 후 엔터 | `/search?q={keyword}` 이동 |
| 태그 클릭 | `/search?tag={tag}` 이동 |
| Repository 만들기 클릭 | `/repositories/new` 이동 (로그인 필요) |

---

## API 연동

### GET /api/v1/repositories?sort=popular&size=12
```
Response 200:
{
  "items": [
    {
      "id": 1,
      "title": "...",
      "description": "...",
      "thumbnail": "...",
      "tags": ["..."],
      "author": { "username": "...", "avatar": "..." },
      "merge_count": 5,
      "created_at": "..."
    }
  ],
  "total": 100,
  "page": 1,
  "size": 12
}
```

### GET /api/v1/repositories?sort=latest&size=12
(동일 구조)

### GET /api/v1/tags/popular
```
Response 200:
{
  "tags": [
    { "id": 1, "name": "판타지" },
    ...
  ]
}
```

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| Repository 없음 | "아직 등록된 작품이 없습니다" 빈 상태 메시지 |
| 네트워크 오류 | "데이터를 불러오지 못했습니다. 다시 시도해주세요" |

---

## 규칙 및 제약

- 인기 기준: Merge 수 + PR 수 등 복합 지표 (구체적 공식은 서버에서 정의)
- 썸네일 없는 Repository는 기본 이미지 표시

---

## 연결 화면

- → Repository 상세 (`/repositories/{repo_id}`)
- → 검색 (`/search`)
- → Repository 생성 (`/repositories/new`)
- → 로그인 (`/login`)
