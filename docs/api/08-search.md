# Search API

Base URL: `/api/v1/search`

---

## GET /api/v1/search

관련 페이지: `pages/03-search`

Repository와 User를 통합 검색한다. 키워드, 태그, 타입, 정렬 기준으로 필터링할 수 있다. MVP에서는 LIKE 검색을 사용하며, 데이터 증가 후 FULLTEXT로 교체 예정이다.

**Endpoint**
```
GET /api/v1/search
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| q | string | N | 검색 키워드. Repository의 제목·설명, User의 username에 LIKE 검색 | `판타지` |
| type | string | N | 검색 타입 (`repository`, `user`, `all`). 기본값: `all` | `repository` |
| sort | string | N | 정렬 기준 (`latest`, `popular`). 기본값: `latest` | `popular` |
| tag | string | N | 태그 필터. Repository 검색에만 적용. 반복 가능 (AND 조건) | `판타지` |
| page | integer | N | 페이지 번호 (기본값: 1) | `1` |
| size | integer | N | 페이지 크기 (기본값: 20, 최대: 100) | `20` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/search?q=판타지&type=repository&sort=popular&tag=마법&page=1&size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| repositories | object | Y | Repository 검색 결과. `type=user`이면 items 빈 배열 | `{...}` |
| repositories.items | array | Y | Repository 목록 | `[...]` |
| repositories.items[].id | integer | Y | Repository ID | `1` |
| repositories.items[].title | string | Y | 작품 제목 | `내 판타지 세계관` |
| repositories.items[].description | string | N | 작품 설명 | `마법이 존재하는 세계의 이야기` |
| repositories.items[].thumbnail | string | N | 썸네일 URL | `https://cdn.example.com/thumb.jpg` |
| repositories.items[].tags | array | Y | 태그 목록 | `["판타지", "마법"]` |
| repositories.items[].author | object | Y | 원작자 정보 | `{...}` |
| repositories.items[].author.username | string | Y | 원작자 username | `creator123` |
| repositories.items[].author.avatar | string | N | 원작자 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| repositories.items[].merge_count | integer | Y | Merge된 기여 수 | `5` |
| repositories.total | integer | Y | 전체 Repository 검색 결과 수 | `50` |
| users | object | Y | User 검색 결과. `type=repository`이면 items 빈 배열 | `{...}` |
| users.items | array | Y | User 목록 | `[...]` |
| users.items[].username | string | Y | username | `contributor123` |
| users.items[].avatar | string | N | 아바타 URL | `https://cdn.example.com/avatar.jpg` |
| users.items[].bio | string | N | 자기소개 | `판타지 기여자입니다.` |
| users.items[].merge_count | integer | Y | Merge된 기여 수 | `3` |
| users.total | integer | Y | 전체 User 검색 결과 수 | `10` |
| page | integer | Y | 현재 페이지 | `1` |
| size | integer | Y | 페이지 크기 | `20` |

**Success Response Example**

200 OK
```json
{
  "repositories": {
    "items": [
      {
        "id": 1,
        "title": "내 판타지 세계관",
        "description": "마법이 존재하는 세계의 이야기",
        "thumbnail": "https://cdn.example.com/thumb.jpg",
        "tags": ["판타지", "마법"],
        "author": {
          "username": "creator123",
          "avatar": "https://cdn.example.com/avatar.jpg"
        },
        "merge_count": 5
      }
    ],
    "total": 50
  },
  "users": {
    "items": [
      {
        "username": "contributor123",
        "avatar": "https://cdn.example.com/avatar.jpg",
        "bio": "판타지 기여자입니다.",
        "merge_count": 3
      }
    ],
    "total": 10
  },
  "page": 1,
  "size": 20
}
```

**Error Response Example**

422 Unprocessable Entity — 유효하지 않은 type 값
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "type은 repository, user, all 중 하나여야 합니다."
  }
}
```

500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "서버 오류가 발생했습니다."
  }
}
```
