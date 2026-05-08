# 사용자 시나리오

WorldBuild의 핵심 흐름을 5개 시나리오로 정리한다.

---

## 시나리오 1 — 원작자: Repository 생성 및 관리

### 목표
자신의 세계관·IP를 WorldBuild에 등록하고, 기여자를 모집할 수 있는 Repository를 구성한다.

### 전제조건
- 회원가입 및 로그인 완료

### 단계별 흐름

| 단계 | 사용자 행동 | 시스템 처리 |
|------|-------------|-------------|
| 1 | "새 Repository 만들기" 버튼 클릭 | Repository 생성 폼 진입 |
| 2 | 제목, 설명, 썸네일, 태그, 외부 링크 입력 | — |
| 3 | README 작성 (주요 캐릭터·지역·세계관 규칙·금지 설정 입력) | — |
| 4 | 모집 영역 선택 (캐릭터 추가, 세계관 설정 등) | — |
| 5 | 기여 가이드라인 작성 후 저장 | `POST /api/v1/repositories` 호출 → Repository 생성, 원작자로 등록 |
| 6 | Repository 상세 페이지로 이동 | 생성된 Repository 정보 반환 |
| 7 | 이후 세계관 보완이 필요하면 수정 | `PATCH /api/v1/repositories/{repo_id}` 호출 → AuditLog(REPO_UPDATE) 기록 |

### 결과
- Repository가 공개 상태로 등록됨
- 컨트리뷰터들이 검색 · 탐색을 통해 발견 가능

### 관련 API
- `POST /api/v1/repositories`
- `PATCH /api/v1/repositories/{repo_id}`
- `GET /api/v1/repositories/{repo_id}`

---

## 시나리오 2 — 컨트리뷰터: PR 작성 · AI 분석 · 제출

### 목표
관심 있는 작품에 캐릭터 아이디어를 제안하고, AI 분석을 거쳐 원작자에게 공식 제출한다.

### 전제조건
- 회원가입 및 로그인 완료
- 대상 Repository가 존재하고 해당 기여 유형을 모집 중

### 단계별 흐름

| 단계 | 사용자 행동 | 시스템 처리 |
|------|-------------|-------------|
| 1 | 검색 또는 탐색으로 작품 발견, Repository 상세 조회 | `GET /api/v1/repositories/{repo_id}` |
| 2 | "기여하기" 버튼 클릭 | `POST /api/v1/repositories/{repo_id}/pull-requests/draft` → `first_drafted_at` 서버 시간으로 기록 (이후 변경 불가) |
| 3 | 자유 형식으로 아이디어 작성 | 30초마다 자동 저장: `PATCH /api/v1/pull-requests/{pr_id}/draft` → `last_saved_at`, `save_count` 갱신, `first_drafted_at` 유지 |
| 4 | "AI 분석 요청" 버튼 클릭 | `POST /api/v1/pull-requests/{pr_id}/ai-analyze` → AI 호출, AiAnalysis 행 생성 |
| 5 | AI 분석 결과 확인 (제목, 요약, 5축 점수, 등급, 충돌 검사 결과) | `GET /api/v1/pull-requests/{pr_id}/ai-analysis` |
| 6 | AI 분석에 대한 자신의 의견 작성 (선택) | `PATCH /api/v1/pull-requests/{pr_id}/contributor-comment` |
| 7 | 공개 여부 설정 후 "최종 제출" 클릭 | `POST /api/v1/pull-requests/{pr_id}/submit` → 상태 DRAFT→SUBMITTED, `submitted_at` 기록, 원작자 알림 생성, AuditLog(PR_SUBMIT) |
| 8 | 제출 완료 화면 및 PR 상세 페이지로 이동 | — |

### 결과
- PR이 SUBMITTED 상태로 원작자에게 전달됨
- `first_drafted_at` (아이디어 최초 작성 시각)이 서버에 영구 보존됨

### 관련 API
- `GET /api/v1/repositories/{repo_id}`
- `POST /api/v1/repositories/{repo_id}/pull-requests/draft`
- `PATCH /api/v1/pull-requests/{pr_id}/draft`
- `POST /api/v1/pull-requests/{pr_id}/ai-analyze`
- `GET /api/v1/pull-requests/{pr_id}/ai-analysis`
- `PATCH /api/v1/pull-requests/{pr_id}/contributor-comment`
- `POST /api/v1/pull-requests/{pr_id}/submit`

---

## 시나리오 3 — 원작자: PR 검토 및 Merge

### 목표
제출된 PR을 검토하고, 우수한 기여를 공식 설정으로 반영하며 컨트리뷰터에게 크레딧을 부여한다.

### 전제조건
- 자신의 Repository에 SUBMITTED 상태 PR이 존재

### 단계별 흐름

| 단계 | 사용자 행동 | 시스템 처리 |
|------|-------------|-------------|
| 1 | 알림 수신 또는 Repository PR 목록에서 PR 확인 | `GET /api/v1/repositories/{repo_id}/pull-requests` |
| 2 | PR 상세 열람 | `GET /api/v1/pull-requests/{pr_id}` → ViewLog INSERT (원작자 != 작성자 조건 충족 시), AuditLog(PR_VIEW) |
| 3 | AI 분석 결과, 5축 점수, 충돌 검사, 컨트리뷰터 의견 검토 | — |
| 4a | 좋은 기여 → "수락" 클릭 | `POST /api/v1/pull-requests/{pr_id}/accept` → SUBMITTED→ACCEPTED, 컨트리뷰터 알림, AuditLog(PR_ACCEPT) |
| 4b | 보완 필요 → "수정 요청" 클릭, 사유 작성 | `POST /api/v1/pull-requests/{pr_id}/request-changes` → SUBMITTED→CHANGES_REQUESTED, 컨트리뷰터 알림, AuditLog(PR_REQUEST_CHANGES) |
| 4c | 부적합 → "거절" 클릭, 카테고리·사유 작성 | `POST /api/v1/pull-requests/{pr_id}/reject` → SUBMITTED→REJECTED, RejectReason INSERT, 컨트리뷰터 알림, AuditLog(PR_REJECT) |
| 5 | 수락 후 공식 반영 결정 → AI 등급 확인, 필요 시 등급 조정 | `POST /api/v1/pull-requests/{pr_id}/grade-override` → AI 등급과 다르면 reason 필수, AuditLog(PR_GRADE_OVERRIDE) |
| 6 | "병합" 클릭, 크레딧 문구·원작자 코멘트 입력 | `POST /api/v1/pull-requests/{pr_id}/merge` → ACCEPTED→MERGED, Merge 행 생성, `citation_url` 생성, ContributorStats/AuthorStats 갱신, 컨트리뷰터 알림, AuditLog(PR_MERGE) |

### 결과
- PR이 MERGED 상태로 공식 기여 이력에 등록됨
- 컨트리뷰터 프로필에 Merge 기록 표시
- `/m/{merge_id}` 퍼머링크로 외부 인용 가능

### 관련 API
- `GET /api/v1/repositories/{repo_id}/pull-requests`
- `GET /api/v1/pull-requests/{pr_id}`
- `POST /api/v1/pull-requests/{pr_id}/accept`
- `POST /api/v1/pull-requests/{pr_id}/request-changes`
- `POST /api/v1/pull-requests/{pr_id}/reject`
- `POST /api/v1/pull-requests/{pr_id}/grade-override`
- `POST /api/v1/pull-requests/{pr_id}/merge`
- `GET /api/v1/merges/{merge_id}`

---

## 시나리오 4 — 탐색자: 검색 및 작품 탐색

### 목표
흥미로운 세계관을 발견하고, 기여할 수 있는 Repository를 찾는다.

### 전제조건
- 로그인 불필요 (공개 Repository 탐색은 누구나 가능)

### 단계별 흐름

| 단계 | 사용자 행동 | 시스템 처리 |
|------|-------------|-------------|
| 1 | 홈 화면에서 인기 Repository 목록 확인 | `GET /api/v1/repositories?sort=popular` |
| 2 | 검색창에 키워드 입력 또는 태그 필터 적용 | `GET /api/v1/search?q=...&type=repository&tag=...` |
| 3 | 검색 결과에서 Repository 클릭 | `GET /api/v1/repositories/{repo_id}` |
| 4 | README, 주요 캐릭터, 모집 영역 확인 | — |
| 5 | Merge된 기여 목록 확인 | `GET /api/v1/repositories/{repo_id}/merges` |
| 6 | 기여자 목록 확인 | `GET /api/v1/repositories/{repo_id}/contributors` |
| 7 | 원작자 프로필 클릭 | `GET /api/v1/users/{username}` |
| 8 | 마음에 들면 로그인 후 기여 시작 | 시나리오 2로 이어짐 |

### 결과
- 원하는 작품을 발견하고 기여 여부를 판단함

### 관련 API
- `GET /api/v1/repositories?sort=popular`
- `GET /api/v1/search`
- `GET /api/v1/repositories/{repo_id}`
- `GET /api/v1/repositories/{repo_id}/merges`
- `GET /api/v1/repositories/{repo_id}/contributors`
- `GET /api/v1/users/{username}`

---

## 시나리오 5 — 분쟁 방지: 작성 시점 보호 · 열람 로그 증명

### 목표
컨트리뷰터가 아이디어 제안 시점을 증명하고, 원작자가 해당 아이디어를 열람했음을 기록으로 확인한다.

### 전제조건
- 컨트리뷰터가 PR을 작성·제출한 상태
- 원작자가 해당 PR을 조회한 상태

### 핵심 보호 메커니즘

#### 작성 시점 보호
- Draft 최초 생성 시 `first_drafted_at`을 **서버 시간**으로 기록
- 이후 자동 저장(`PATCH /draft`)이 반복되어도 `first_drafted_at`은 절대 갱신되지 않음
- 클라이언트가 보낸 시간 값은 신뢰하지 않음
- 제출 시점(`submitted_at`)도 서버 시간으로 기록

#### 열람 로그 보호
- 원작자가 `GET /pull-requests/{pr_id}`를 호출하면 자동으로 ViewLog 행이 INSERT됨
- ViewLog는 UPDATE/DELETE 불가 (서비스 레이어에서 강제)
- 같은 PR을 여러 번 열람하면 매번 별도 행이 쌓임
- ViewLog 항목: `pull_request_id`, `viewer_id`, `viewed_at`, `ip_hash`, `day_bucket_hash`
- 모든 열람 행위는 AuditLog(PR_VIEW)에도 기록됨

#### Reject 사유 보존
- Reject 사유는 영구 보존 (DELETE 불가)
- 사유 변경이 필요한 경우 새 RejectReason 행을 추가하고 이전 행의 `superseded_by_id`를 채움 (이력 체인 유지)
- 컨트리뷰터는 언제든 자신의 PR Reject 사유를 조회 가능

### 증명 가능한 사실
| 증명 대상 | 근거 |
|-----------|------|
| "나는 이 날짜에 아이디어를 처음 작성했다" | `PullRequest.first_drafted_at` (서버 시간, 불변) |
| "나는 이 날짜에 제출했다" | `PullRequest.submitted_at` (서버 시간) |
| "원작자가 이 날짜에 내 PR을 열람했다" | `ViewLog.viewed_at` + `AuditLog` (삭제 불가) |
| "원작자가 이 이유로 거절했다" | `RejectReason` (삭제 불가, 변경 이력 보존) |
| "이 PR이 공식 반영되었다" | `Merge.citation_url` (퍼머링크) |
