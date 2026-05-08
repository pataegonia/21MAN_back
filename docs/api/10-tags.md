# Tags API

Base URL: `/api/v1/tags`

---

## GET /api/v1/tags

관련 페이지: `pages/03-search`, `pages/06-repository-create`, `pages/07-repository-edit`

태그를 키워드로 검색한다. Repository 생성·수정 폼의 태그 자동완성 및 검색 페이지의 필터용으로 사용된다.

**Endpoint**
```
GET /api/v1/tags
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| q | string | N | 검색 키워드. 태그 이름에 LIKE 검색 | `판타` |
| size | integer | N | 반환할 최대 개수 (기본값: 10, 최대: 50) | `10` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/tags?q=판타&size=10
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| tags | array | Y | 태그 목록 | `[...]` |
| tags[].id | integer | Y | 태그 ID | `1` |
| tags[].name | string | Y | 태그 이름 | `판타지` |

**Success Response Example**

200 OK
```json
{
  "tags": [
    { "id": 1, "name": "판타지" },
    { "id": 7, "name": "판타스틱" }
  ]
}
```

**Error Response Example**

500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "서버 오류가 발생했습니다."
  }
}
```

---

## GET /api/v1/tags/popular

관련 페이지: `pages/02-home`, `pages/03-search`

사용 빈도가 높은 인기 태그 목록을 반환한다. 홈 화면의 인기 태그 섹션과 검색 페이지 퀵 선택용으로 사용된다.

**Endpoint**
```
GET /api/v1/tags/popular
```

**Path Parameter**

(없음)

**Query Parameter**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| size | integer | N | 반환할 최대 개수 (기본값: 20, 최대: 50) | `20` |

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**
```
GET /api/v1/tags/popular?size=20
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| tags | array | Y | 인기 태그 목록 (사용 빈도 내림차순) | `[...]` |
| tags[].id | integer | Y | 태그 ID | `1` |
| tags[].name | string | Y | 태그 이름 | `판타지` |
| tags[].repository_count | integer | Y | 해당 태그를 사용하는 Repository 수 | `42` |

**Success Response Example**

200 OK
```json
{
  "tags": [
    { "id": 1, "name": "판타지", "repository_count": 42 },
    { "id": 2, "name": "SF", "repository_count": 28 },
    { "id": 3, "name": "마법", "repository_count": 21 }
  ]
}
```

**Error Response Example**

500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "서버 오류가 발생했습니다."
  }
}
```
