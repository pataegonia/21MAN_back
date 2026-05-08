# User 테이블

## 테이블 설명

서비스 사용자 계정 정보를 저장한다. 원작자와 컨트리뷰터를 구분하지 않고 단일 테이블로 관리하며, 역할은 Repository의 author_id 참조로 결정된다.

## 테이블 이름

`users`

## 컬럼 명세

| Key | Name | Type | Constraint | Description | Example |
|-----|------|------|------------|-------------|---------|
| PK | id | BIGINT | NOT NULL AUTO_INCREMENT | 사용자 고유 ID | `1` |
| - | email | VARCHAR(255) | NOT NULL UNIQUE | 로그인에 사용하는 이메일 | `user@example.com` |
| - | password_hash | VARCHAR(255) | NOT NULL | bcrypt 등으로 해시된 비밀번호 | `$2b$12$...` |
| - | username | VARCHAR(30) | NOT NULL UNIQUE | 공개 식별자. 영문·숫자·언더스코어 3~30자 | `creator123` |
| - | avatar | VARCHAR(500) | NULL | 프로필 이미지 URL | `https://cdn.example.com/avatar.jpg` |
| - | bio | VARCHAR(200) | NULL | 자기소개 | `판타지 세계관을 만드는 작가입니다.` |
| - | is_active | BOOLEAN | NOT NULL DEFAULT TRUE | 계정 활성 여부. FALSE면 탈퇴 처리된 계정 | `TRUE` |
| - | created_at | DATETIME(6) | NOT NULL | 계정 생성 시각 (UTC) | `2024-01-01 00:00:00.000000` |
| - | updated_at | DATETIME(6) | NOT NULL | 마지막 수정 시각 (UTC) | `2024-06-01 00:00:00.000000` |

### 인덱스

| 종류 | 컬럼 | 설명 |
|------|------|------|
| UNIQUE | email | 이메일 중복 방지 |
| UNIQUE | username | username 중복 방지 |

## Example Row

```json
{
  "id": 1,
  "email": "user@example.com",
  "password_hash": "$2b$12$eImiTXuWVxfM37uY4JANjO...",
  "username": "creator123",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "bio": "판타지 세계관을 만드는 작가입니다.",
  "is_active": true,
  "created_at": "2024-01-01 00:00:00.000000",
  "updated_at": "2024-06-01 00:00:00.000000"
}
```
