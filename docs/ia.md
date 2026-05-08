# Information Architecture (IA)

WorldBuild 서비스의 전체 화면 계층 구조, 접근 권한, API 매핑을 정리한다.

---

## 권한 범례

| 기호 | 의미 |
|------|------|
| 🌐 | 비로그인 포함 누구나 접근 가능 |
| 🔑 | 로그인한 사용자만 접근 가능 |
| ✍️ | PR 작성자 본인만 접근 가능 |
| 👑 | 해당 Repository의 원작자만 접근 가능 |

---

## 화면 계층 구조

```
WorldBuild
│
├── 🌐 홈 (/)
│   ├── 인기 Repository 목록
│   ├── 최신 Repository 목록
│   └── 검색창
│
├── 🌐 검색 (/search)
│   ├── 통합 검색 결과 (Repository + User)
│   ├── Repository 필터 (태그, 모집 영역, 정렬)
│   └── User 필터 (기여자 / 원작자)
│
├── 인증
│   ├── 🌐 회원가입 (/register)
│   ├── 🌐 로그인 (/login)
│   └── 🔑 로그아웃 (action)
│
├── Repository
│   ├── 🌐 목록 (/repositories)
│   ├── 🌐 상세 (/repositories/{repo_id})
│   │   ├── README 탭
│   │   ├── Merge 이력 탭 (/repositories/{repo_id}/merges)
│   │   └── 기여자 탭 (/repositories/{repo_id}/contributors)
│   ├── 🔑 생성 (/repositories/new)
│   └── 👑 수정 (/repositories/{repo_id}/edit)
│
├── Pull Request
│   ├── 🔑 PR 작성 — Draft (/repositories/{repo_id}/pull-requests/new)
│   │   ├── 자유 작성 에디터
│   │   ├── AI 분석 요청 패널
│   │   └── 컨트리뷰터 의견 입력
│   ├── 🔑 PR 작성 — 제출 확인 (/pull-requests/{pr_id}/submit)
│   ├── 🌐+ PR 상세 (/pull-requests/{pr_id})
│   │   ├── 기본 정보 및 원문
│   │   ├── AI 분석 결과 패널
│   │   ├── 충돌 검사 패널
│   │   ├── ViewLog 표시 (작성자 본인이면 열람 기록 확인 가능)
│   │   └── 👑 원작자 검토 액션 패널
│   └── 🌐+ PR 목록 (/repositories/{repo_id}/pull-requests)
│
├── 사용자 프로필
│   ├── 🌐 공개 프로필 (/users/{username})
│   │   ├── 기본 정보 탭
│   │   ├── 생성한 Repository 탭 (/users/{username}/repositories)
│   │   ├── 기여 내역 탭 (/users/{username}/contributions)
│   │   └── 통계 탭 (/users/{username}/stats/contributor, /stats/author)
│   └── 🔑 내 프로필 (/me 또는 /users/{my-username})
│       ├── 내 PR 전체 목록 (/users/{username}/pull-requests)
│       └── 뱃지 (/users/{username}/badges)
│
├── 🔑 알림 (/notifications)
│   ├── 전체 알림 목록
│   └── 읽지 않은 알림 필터
│
└── 🌐 Merge 퍼머링크 (/m/{merge_id})
    └── 병합된 기여의 공개 인용 페이지
```

---

## 화면별 API 매핑

### 홈 (/)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 인기 Repository 목록 | GET | `/api/v1/repositories?sort=popular` | 🌐 |
| 최신 Repository 목록 | GET | `/api/v1/repositories?sort=latest` | 🌐 |

---

### 검색 (/search)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 통합 검색 | GET | `/api/v1/search?q=...&type=all&sort=...&tag=...` | 🌐 |
| 인기 태그 | GET | `/api/v1/tags/popular` | 🌐 |
| 태그 자동완성 | GET | `/api/v1/tags?q=...` | 🌐 |

---

### 인증

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 회원가입 | POST | `/api/v1/auth/register` | 🌐 |
| 로그인 | POST | `/api/v1/auth/login` | 🌐 |
| 토큰 갱신 | POST | `/api/v1/auth/refresh` | 🌐 |
| 로그아웃 | POST | `/api/v1/auth/logout` | 🔑 |
| 현재 사용자 조회 | GET | `/api/v1/auth/me` | 🔑 |

---

### Repository 목록 (/repositories)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 목록·검색 | GET | `/api/v1/repositories?q=...&tag=...&sort=...` | 🌐 |

---

### Repository 상세 (/repositories/{repo_id})

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| Repository 상세 | GET | `/api/v1/repositories/{repo_id}` | 🌐 |
| Merge 이력 | GET | `/api/v1/repositories/{repo_id}/merges` | 🌐 |
| 기여자 목록 | GET | `/api/v1/repositories/{repo_id}/contributors` | 🌐 |
| PR 목록 | GET | `/api/v1/repositories/{repo_id}/pull-requests` | 🌐+ |
| Repository 통계 | GET | `/api/v1/repositories/{repo_id}/stats` | 👑 |

---

### Repository 생성 (/repositories/new)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| Repository 생성 | POST | `/api/v1/repositories` | 🔑 |
| 태그 자동완성 | GET | `/api/v1/tags?q=...` | 🌐 |

---

### Repository 수정 (/repositories/{repo_id}/edit)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| Repository 수정 | PATCH | `/api/v1/repositories/{repo_id}` | 👑 |

---

### PR 작성 — Draft

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| Draft 생성 | POST | `/api/v1/repositories/{repo_id}/pull-requests/draft` | 🔑 |
| Draft 조회 | GET | `/api/v1/pull-requests/{pr_id}/draft` | ✍️ |
| 자동 저장 | PATCH | `/api/v1/pull-requests/{pr_id}/draft` | ✍️ |
| AI 분석 요청 | POST | `/api/v1/pull-requests/{pr_id}/ai-analyze` | ✍️ |
| AI 분석 결과 조회 | GET | `/api/v1/pull-requests/{pr_id}/ai-analysis` | ✍️, 👑 |
| 컨트리뷰터 의견 저장 | PATCH | `/api/v1/pull-requests/{pr_id}/contributor-comment` | ✍️ |

---

### PR 제출 확인

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 최종 제출 | POST | `/api/v1/pull-requests/{pr_id}/submit` | ✍️ |

---

### PR 상세 (/pull-requests/{pr_id})

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| PR 상세 조회 | GET | `/api/v1/pull-requests/{pr_id}` | 🌐+, 자동 ViewLog |
| AI 분석 결과 조회 | GET | `/api/v1/pull-requests/{pr_id}/ai-analysis` | ✍️, 👑 |
| 수락 | POST | `/api/v1/pull-requests/{pr_id}/accept` | 👑 |
| 수정 요청 | POST | `/api/v1/pull-requests/{pr_id}/request-changes` | 👑 |
| 거절 | POST | `/api/v1/pull-requests/{pr_id}/reject` | 👑 |
| 병합 | POST | `/api/v1/pull-requests/{pr_id}/merge` | 👑 |
| 등급 조정 | POST | `/api/v1/pull-requests/{pr_id}/grade-override` | 👑 |
| Reject 사유 수정 | PATCH | `/api/v1/pull-requests/{pr_id}/reject-reason` | 👑 |

---

### 사용자 공개 프로필 (/users/{username})

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 기본 프로필 | GET | `/api/v1/users/{username}` | 🌐 |
| 생성한 Repository | GET | `/api/v1/users/{username}/repositories` | 🌐 |
| Merge된 기여 목록 | GET | `/api/v1/users/{username}/contributions` | 🌐 |
| PR 목록 | GET | `/api/v1/users/{username}/pull-requests` | 🌐+(본인=전체, 타인=PUBLIC) |
| 컨트리뷰터 통계 | GET | `/api/v1/users/{username}/stats/contributor` | 🌐 |
| 원작자 통계 | GET | `/api/v1/users/{username}/stats/author` | 🌐 |
| 뱃지 | GET | `/api/v1/users/{username}/badges` | 🌐 |

---

### 알림 (/notifications)

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| 알림 목록 | GET | `/api/v1/notifications` | 🔑 |
| 읽지 않은 수 | GET | `/api/v1/notifications/unread-count` | 🔑 |
| 단건 읽음 처리 | POST | `/api/v1/notifications/{id}/read` | 🔑 |
| 전체 읽음 처리 | POST | `/api/v1/notifications/read-all` | 🔑 |

---

### Merge 퍼머링크 (/m/{merge_id})

| 목적 | Method | Path | 권한 |
|------|--------|------|------|
| Merge 정보 조회 | GET | `/api/v1/merges/{merge_id}` | 🌐 |

---

## PR 상태 전이 다이어그램

```
                    ┌──────────────┐
                    │    DRAFT     │
                    └──────┬───────┘
                           │ 컨트리뷰터 제출
                           ▼
                    ┌──────────────┐
              ┌────▶│  SUBMITTED   │◀────────────────┐
              │     └──────┬───────┘                 │
              │            │                         │
              │     ┌──────┴───────────────┐         │
              │     ▼         ▼            ▼         │
              │ ┌────────┐ ┌──────────────┐ ┌────────┴──┐
              │ │ACCEPTED│ │CHANGES_REQ..│ │ REJECTED  │
              │ └────┬───┘ └──────┬───────┘ └───────────┘
              │      │            │ 컨트리뷰터 재제출
              │      │            └──────────────────────┘
              │      │ 병합
              │      ▼
              │ ┌────────┐
              └─│ MERGED │
                └────────┘

허용 전이:
  DRAFT → SUBMITTED
  SUBMITTED → ACCEPTED
  SUBMITTED → CHANGES_REQUESTED
  SUBMITTED → REJECTED
  SUBMITTED → MERGED
  ACCEPTED → MERGED
  CHANGES_REQUESTED → SUBMITTED

금지 전이:
  REJECTED → MERGED
  MERGED → 모든 상태
```

---

## 알림 유형 목록

| 유형 | 수신자 | 발생 시점 |
|------|--------|-----------|
| `PR_SUBMITTED` | 원작자 | 컨트리뷰터가 PR 제출 |
| `PR_RESUBMITTED` | 원작자 | CHANGES_REQUESTED → SUBMITTED 재제출 |
| `PR_COMMENT_ADDED` | 원작자 | 컨트리뷰터 의견 추가 |
| `PR_ACCEPTED` | 컨트리뷰터 | 원작자가 수락 |
| `PR_CHANGES_REQUESTED` | 컨트리뷰터 | 원작자가 수정 요청 |
| `PR_REJECTED` | 컨트리뷰터 | 원작자가 거절 |
| `PR_MERGED` | 컨트리뷰터 | 원작자가 병합 |
| `GRADE_ADJUSTED` | 컨트리뷰터 | 원작자가 등급 조정 |

---

## AuditLog 액션 유형

| 액션 | 발생 조건 |
|------|-----------|
| `PR_SUBMIT` | PR 최종 제출 |
| `PR_VIEW` | 원작자가 PR 열람 |
| `PR_ACCEPT` | 원작자가 PR 수락 |
| `PR_REQUEST_CHANGES` | 원작자가 수정 요청 |
| `PR_REJECT` | 원작자가 PR 거절 |
| `PR_MERGE` | 원작자가 PR 병합 |
| `PR_GRADE_OVERRIDE` | 원작자가 등급 조정 |
| `REPO_UPDATE` | Repository 주요 정보 수정 |
