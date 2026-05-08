# 13 — 사용자 공개 프로필

## 개요

특정 사용자의 공개 프로필 페이지. 생성한 Repository, Merge된 기여, 통계, 뱃지를 표시한다.

---

## 접근 권한

🌐 누구나 (단, PR 목록은 PUBLIC만 표시)
본인이 조회하는 경우 전체 PR 표시

---

## 화면 구성요소

### 프로필 헤더
- 아바타 이미지
- username
- bio (자기소개)
- 가입일
- 컨트리뷰터 통계 요약: 전체 PR 수, Merge 수, Merge 비율
- 원작자 통계 요약: Repository 수, 받은 PR 수

### 탭 네비게이션
- 생성한 Repository
- 기여 내역 (Merge된 PR)
- 뱃지

### 생성한 Repository 탭
- Repository 카드 목록 (썸네일, 제목, 태그, Merge 수, PR 수)

### 기여 내역 탭
- Merge된 PR 목록
- 각 항목: Repository 이름, PR 제목, 최종 등급 뱃지, 병합일
- 등급별 필터: MAJOR / NORMAL / MINOR
- 클릭 시 `/m/{merge_id}` 또는 `/pull-requests/{pr_id}`

### 뱃지 탭
- 획득한 뱃지 목록 (MVP에서는 빈 배열 반환 가능)
- 각 뱃지: 아이콘, 이름, 획득 조건, 획득일

### 통계 섹션 (선택적으로 표시)
- Contributor 통계: 전체 PR / Merge / Major·Normal·Minor 수 / Merge 비율
- Author 통계: Repository 수 / 받은 PR / Merge한 PR / Merge 비율 / 평균 검토 기간

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| Repository 카드 클릭 | `/repositories/{repo_id}` 이동 |
| 기여 항목 클릭 | Merge 퍼머링크 또는 PR 상세 이동 |
| 탭 전환 | 해당 탭 데이터 조회 |
| 등급 필터 선택 | 해당 등급 기여만 표시 |

---

## API 연동

### GET /api/v1/users/{username}
```
Response 200:
{
  "id": 1,
  "username": "creator123",
  "avatar": "https://...",
  "bio": "판타지 세계관을 만드는 작가입니다.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/users/{username}/repositories?page=1&size=20
```
Response 200:
{
  "items": [
    {
      "id": 1,
      "title": "...",
      "thumbnail": "...",
      "tags": ["..."],
      "merge_count": 5,
      "pr_count": 12
    }
  ],
  "total": 3
}
```

### GET /api/v1/users/{username}/contributions?page=1&size=20&grade=MAJOR
Merge된 기여 목록.
```
Response 200:
{
  "items": [
    {
      "merge_id": 5,
      "pull_request": { "id": 42, "title": "..." },
      "repository": { "id": 1, "title": "..." },
      "final_grade": "MAJOR",
      "merged_at": "2024-01-03T12:00:00Z"
    }
  ],
  "total": 10
}
```

### GET /api/v1/users/{username}/stats/contributor
```
Response 200:
{
  "total_prs": 15,
  "merged_prs": 8,
  "major_count": 2,
  "normal_count": 4,
  "minor_count": 2,
  "merge_ratio": 0.53,
  "last_activity_at": "2024-06-01T00:00:00Z"
}
```

### GET /api/v1/users/{username}/stats/author
```
Response 200:
{
  "repository_count": 3,
  "received_prs": 25,
  "merged_prs": 12,
  "merge_ratio": 0.48,
  "avg_review_days": 2.5,
  "last_activity_at": "2024-06-01T00:00:00Z"
}
```

### GET /api/v1/users/{username}/badges
```
Response 200:
{
  "badges": []
}
```
MVP에서는 빈 배열 반환 가능.

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 사용자 없음 (404) | "존재하지 않는 사용자입니다" |
| Repository 없음 | "아직 등록한 작품이 없습니다" |
| 기여 없음 | "아직 Merge된 기여가 없습니다" |

---

## 규칙 및 제약

- PR 목록: 본인이면 전체 조회, 타인이면 PUBLIC만 조회
- 통계는 on-demand 집계 쿼리로 계산 (별도 테이블 없음)
- Merge 비율: `merged_prs / (total_prs - draft_count)` 또는 제출된 PR 대비
- 뱃지는 MVP에서 빈 배열 반환 허용, 추후 기준 추가

---

## 연결 화면

- → Repository 상세 (`/repositories/{repo_id}`)
- → Merge 퍼머링크 (`/m/{merge_id}`)
- → PR 상세 (`/pull-requests/{pr_id}`)
