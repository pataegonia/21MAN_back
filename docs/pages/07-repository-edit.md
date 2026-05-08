# 07 — Repository 수정

## 개요

원작자가 등록한 Repository의 정보와 README를 수정하는 페이지. 수정 시 AuditLog(REPO_UPDATE)가 기록된다.

---

## 접근 권한

👑 해당 Repository의 원작자만

---

## 화면 구성요소

생성 폼과 동일한 구조이며, 기존 값이 미리 채워진 상태로 진입한다.

### 기본 정보 섹션
- 제목 (기존 값 표시)
- 설명
- 썸네일 (현재 이미지 표시, 변경 가능)
- 태그 (현재 태그 표시)
- 외부 링크

### README 섹션
- 작품 설명 (마크다운 에디터, 기존 내용 표시)
- 주요 캐릭터 목록 (기존 목록 표시, 추가/삭제 가능)
- 주요 지역 목록
- 핵심 세계관 규칙 목록
- 금지 설정 목록

### 모집 설정 섹션
- 모집 영역 (현재 선택 상태 표시)
- 기여 가이드라인

### 저장 버튼
- "변경사항 저장"
- "취소" (변경사항 버리고 상세 페이지로 이동)

---

## 사용자 액션

| 액션 | 결과 |
|------|------|
| 필드 수정 | 로컬 상태 업데이트 |
| 저장 | 유효성 검사 → PATCH API 호출 → Repository 상세로 이동 |
| 취소 | 변경사항 버리고 Repository 상세로 이동 |

---

## API 연동

### GET /api/v1/repositories/{repo_id}
페이지 진입 시 기존 데이터 로드.

### PATCH /api/v1/repositories/{repo_id}
```
Header: Authorization: Bearer {access_token}

Request:
{
  "title": "수정된 제목",
  "description": "수정된 설명",
  "thumbnail": "https://...",
  "tags": ["판타지"],
  "external_links": ["https://..."],
  "readme": {
    "content": "## 수정된 세계관\n...",
    "characters": [
      { "name": "아르카", "description": "수정된 설명" }
    ],
    "regions": [...],
    "world_rules": [...],
    "forbidden_settings": [...]
  },
  "recruiting_areas": ["character_add"],
  "contribution_guidelines": "## 수정된 가이드\n..."
}

Response 200:
{
  "id": 1,
  "title": "수정된 제목",
  ...
}
```
모든 자식 컬렉션(characters, regions, world_rules, forbidden_settings, recruiting_areas)은 배열 통째로 교체(replace) 방식이다. 부분 갱신이 없어 충돌이 발생하지 않는다.

---

## 상태 처리

| 상태 | 처리 |
|------|------|
| 권한 없음 (403) | "수정 권한이 없습니다" → Repository 상세로 이동 |
| 저장 실패 | "저장에 실패했습니다. 다시 시도해주세요" |
| 저장 성공 | "저장되었습니다" 토스트 → Repository 상세로 이동 |

---

## 규칙 및 제약

- 원작자 이외의 사용자가 접근하면 403 반환
- `PATCH` 요청 후 서버는 AuditLog(`REPO_UPDATE`) 기록
- 모든 자식 컬렉션(캐릭터, 지역, 규칙 등)은 전체 배열 교체 방식으로 저장
- 단건 수정 엔드포인트 없음 — 항상 전체 PATCH

---

## 연결 화면

- 저장 성공 → Repository 상세 (`/repositories/{repo_id}`)
- 취소 → Repository 상세 (`/repositories/{repo_id}`)
