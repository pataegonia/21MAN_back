# API 테스트 결과 — 07. Merges 조회

테스트 일시: 2026-05-09  
서버: `http://127.0.0.1:8000`  
테스트 계정: `testauthor` (user_id: 1, repo author), `otheruser` (user_id: 2)  
테스트 Merge: id=4 (PR#6, AI 분석 포함 전체 플로우)

---

## 결과 요약

| # | Method | Endpoint | Status | 결과 |
|---|--------|----------|--------|------|
| 1 | GET | `/merges/4` (AI 분석 포함 merge) | **200** | ✅ |
| E1 | GET | `/merges/999` (존재하지 않는 merge) | **404** MERGE_NOT_FOUND | ✅ |
| E2 | POST | `/pull-requests/{id}/merge` (AI 분석 없음) | **400** AI_ANALYSIS_REQUIRED | ✅ |

전체 3개 케이스 통과.

---

## 테스트 플로우 (PR#6)

```
Draft 생성 → 내용 저장 → AI 분석 → 제출 → 수락 → 병합 → GET /merges/4
```

---

## 1. GET `/merges/{merge_id}` — 200 OK

**Request**
```
GET /api/v1/merges/4
```

**Response**
```json
{
  "id": 4,
  "pull_request": {
    "id": 6,
    "title": "첫 번째 드래곤 기사 세리우스 소개",
    "summary": "세리우스는 인간과 드래곤의 언약으로 태어난 반드래곤 존재로, 드래곤의 화염 마법과 인간의 검술을 결합한 전투 방식을 사용하여 어둠의 군주에 맞서는 전사입니다.",
    "contribution_types": ["character_add"],
    "first_drafted_at": "2026-05-08T16:50:44",
    "submitted_at": "2026-05-08T16:51:15"
  },
  "repository": {
    "id": 1,
    "title": "테스트 판타지 세계관",
    "thumbnail": null
  },
  "contributor": {
    "username": "otheruser",
    "avatar": null
  },
  "author": {
    "username": "testauthor",
    "avatar": null
  },
  "final_grade": "MAJOR",
  "credit_text": "세리우스: 첫 드래곤 기사 — 기여: @otheruser",
  "author_comment": "공식 설정 반영.",
  "citation_url": "https://worldbuild.example.com/m/4",
  "merged_at": "2026-05-08T16:51:15"
}
```

---

## 에러 케이스

### 404 — 존재하지 않는 merge
```json
{ "error": { "code": "MERGE_NOT_FOUND", "message": "존재하지 않는 기여 기록입니다." } }
```

### 400 — AI 분석 없이 merge 시도
```json
{ "error": { "code": "AI_ANALYSIS_REQUIRED", "message": "PR 병합 전 AI 분석이 필요합니다." } }
```
