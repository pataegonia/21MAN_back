# API 테스트 결과 — 10. Tags 조회

테스트 일시: 2026-05-09  
서버: `http://127.0.0.1:8000`  
인증: 불필요 (공개 API)

---

## 결과 요약

| # | Method | Endpoint | Status | 결과 |
|---|--------|----------|--------|------|
| 1 | GET | `/tags?q=판타&size=10` | **200** | ✅ |
| 2 | GET | `/tags` (q 없음, 기본 size=10) | **200** | ✅ |
| 3 | GET | `/tags/popular?size=5` | **200** | ✅ |

전체 3개 케이스 통과.

---

## 테스트 데이터

```sql
INSERT INTO tags (name) VALUES ('판타지'), ('SF'), ('마법'), ('판타스틱'), ('현대'), ('로맨스'), ('스릴러');
INSERT INTO repository_tags (repository_id, tag_id)
  SELECT 1, id FROM tags WHERE name IN ('판타지', '마법');
```

---

## 1. GET `/tags?q=판타&size=10` — 200 OK

**Request**
```
GET /api/v1/tags?q=판타&size=10
```

**Response**
```json
{
  "tags": [
    { "id": 4, "name": "판타스틱" },
    { "id": 1, "name": "판타지" }
  ]
}
```

LIKE `%판타%` 검색, 이름 알파벳순 정렬.

---

## 2. GET `/tags` — 200 OK

**Request**
```
GET /api/v1/tags
```

**Response**
```json
{
  "tags": [
    { "id": 2, "name": "SF" },
    { "id": 6, "name": "로맨스" },
    { "id": 3, "name": "마법" },
    { "id": 7, "name": "스릴러" },
    { "id": 4, "name": "판타스틱" },
    { "id": 1, "name": "판타지" },
    { "id": 5, "name": "현대" }
  ]
}
```

q 파라미터 없이 전체 조회, 기본 size=10.

---

## 3. GET `/tags/popular?size=5` — 200 OK

**Request**
```
GET /api/v1/tags/popular?size=5
```

**Response**
```json
{
  "tags": [
    { "id": 1, "name": "판타지", "repository_count": 1 },
    { "id": 3, "name": "마법", "repository_count": 1 }
  ]
}
```

repository_tags 기준 사용 빈도 내림차순, repository_count 포함.  
사용 중인 태그만 반환 (INNER JOIN).
