<p align="center">
  <strong>서랍 Backend</strong>
</p>

<p align="center">
  창작자가 만든 세계관에 외부 기여자가 아이디어 PR을 보내고, 원작자가 검토해 공식 설정으로 반영하는 창작 협업 플랫폼 API
  프론트 링크 : https://github.com/k3vin7/21MAN_front
</p>

<p align="center">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-8.x-4479A1?style=flat-square">
  <img alt="Auth" src="https://img.shields.io/badge/Auth-JWT%20%2B%20Refresh-black?style=flat-square">
</p>

---

## What Is 서랍?

서랍는 창작 IP를 위한 GitHub 같은 협업 플랫폼입니다.

개발자가 Repository와 Pull Request로 코드를 협업하듯, 창작자는 서랍에서 작품 Repository를 만들고 외부 기여자는 캐릭터, 설정, 사건, 장소 아이디어를 PR로 제안합니다. 원작자는 AI 분석 결과와 충돌 가능성을 참고해 제안을 수락, 수정 요청, 거절, 병합할 수 있습니다.

핵심은 단순 아이디어 게시판이 아니라, 창작 시점과 열람 기록, 거절 사유, 병합 이력을 남기는 신뢰 가능한 협업 흐름입니다.

## Core Features

| Domain | Status | Description |
|---|---|---|
| Auth | MVP | Email/password 회원가입, JWT access token, opaque refresh token rotation |
| Users | MVP | 공개 프로필, 생성한 Repository, 제출 PR, Merge 통계 |
| Repository | MVP | 세계관 생성, README 구조화, 태그, 모집 영역, contributor/merge 조회 |
| Pull Request | MVP | Draft 자동 저장, 제출, 공개/비공개 조회 권한, 원작자 액션 |
| AI Analysis | MVP | PR 요약, 구조화, 5축 점수, 등급, 충돌 검사 결과 저장 |
| Trust Logs | MVP | ViewLog, AuditLog, RejectReason 영구 기록 |
| Merge | MVP | 공식 반영 기록, 크레딧, permalink |
| Notifications | MVP | REST polling 기반 인앱 알림 |
| Search | MVP | Repository/User 통합 검색, 태그/원작자/모집 영역 필터 |

## Architecture

```mermaid
flowchart LR
  Client[Frontend] --> API[FastAPI API]
  API --> Auth[Auth Service]
  API --> Repo[Repository Service]
  API --> PR[Pull Request Service]
  API --> Notify[Notification Service]
  API --> Search[Search Service]
  PR --> AI[OpenAI Analysis]
  Auth --> DB[(MySQL)]
  Repo --> DB
  PR --> DB
  Notify --> DB
  Search --> DB
```

```mermaid
erDiagram
  User ||--o{ Repository : authors
  User ||--o{ PullRequest : submits
  Repository ||--o{ PullRequest : receives
  Repository ||--o{ RepoCharacter : has
  Repository ||--o{ RepoRegion : has
  Repository ||--o{ RepoRule : has
  Repository ||--o{ RepoForbidden : has
  Repository ||--o{ RecruitingArea : has
  Repository ||--o{ RepositoryTag : tagged
  Tag ||--o{ RepositoryTag : maps
  PullRequest ||--o{ AiAnalysis : analyzed
  AiAnalysis ||--o{ ConflictCheck : checks
  PullRequest ||--o{ ViewLog : viewed
  PullRequest ||--o{ RejectReason : rejected
  PullRequest ||--o| Merge : merged
  User ||--o{ Notification : receives
  User ||--o{ AuditLog : acts
```

## Tech Stack

| Area | Stack |
|---|---|
| Web | FastAPI, Uvicorn |
| Database | MySQL |
| ORM / Migration | SQLAlchemy 2.0, Alembic |
| Auth | Email/password, JWT access token, opaque refresh token |
| AI | OpenAI API |
| Validation | Pydantic |
| Notifications | REST polling |

## Quick Start

### 1. Create Virtual Environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

macOS, Linux, WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Environment

`.env`에서 로컬 DB와 secret 값을 설정합니다.

```env
APP_DEBUG=true
DATABASE_URL=mysql+pymysql://worldbuild:worldbuild@localhost:3306/worldbuild
JWT_SECRET=dev-change-this-jwt-secret-at-least-32-bytes
IP_HASH_SECRET=dev-change-this-ip-secret-at-least-32-bytes
OPENAI_API_KEY=
```

AI 분석 엔드포인트를 실제로 호출하려면 `OPENAI_API_KEY`가 필요합니다.

### 3. Run Migrations

```bash
alembic upgrade head
```

Alembic 명령이 잡히지 않으면 venv가 활성화되어 있는지 먼저 확인하세요.

### 4. Start API Server

```bash
uvicorn app.main:app --reload
```

| Service | URL |
|---|---|
| API root | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/api/v1/health |

## Demo Data

시연용 유저와 세계관은 seed script로 생성할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\seed_demo_data.py
```

생성되는 주요 계정:

| Role | Email | Password | Username |
|---|---|---|---|
| 원작자 | `demo.author@worldbuild-demo.com` | `Demo1234!` | `demo_author` |
| 컨트리뷰터 | `demo.contributor@worldbuild-demo.com` | `Demo1234!` | `demo_contributor` |

추천 시연 플로우:

1. `demo_contributor`로 로그인
2. `별빛 기록관` Repository에 PR 작성 및 제출
3. `demo_author`로 로그인
4. `/r/{repo_id}/dashboard`에서 PR 검토
5. Accept 또는 Merge 처리

## API Map

Base path: `/api/v1`

| Domain | Endpoints |
|---|---|
| Auth | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me` |
| Users | `/users/{username}`, `/users/{username}/repositories`, `/users/{username}/pull-requests`, `/users/{username}/stats/*` |
| Repositories | `/repositories`, `/repositories/{repo_id}`, `/repositories/{repo_id}/dashboard`, `/repositories/{repo_id}/stats` |
| Pull Requests | `/repositories/{repo_id}/pull-requests/draft`, `/pull-requests/{pr_id}`, `/pull-requests/{pr_id}/submit` |
| Author Actions | `/pull-requests/{pr_id}/accept`, `/request-changes`, `/reject`, `/merge`, `/grade-override` |
| Search | `/search`, `/tags`, `/tags/popular` |
| Notifications | `/notifications`, `/notifications/unread-count`, `/notifications/{id}/read` |
| Merge | `/merges/{merge_id}` |

Detailed specs live in [`docs/api`](docs/api).

## Project Layout

```text
app/
  api/
    routes/           # FastAPI routers
  core/               # config, security, exception handling
  db/                 # SQLAlchemy base and session
  models/             # SQLAlchemy models
  repositories/       # data-access queries
  schemas/            # Pydantic request/response schemas
  services/           # business logic
  main.py
alembic/              # DB migrations
docs/
  api/                # endpoint specs
  db/                 # table specs
  pages/              # frontend page/API mapping
scripts/
  seed_demo_data.py   # local demo seed
```

## Trust & Safety Model

서랍은 창작 협업에서 생길 수 있는 분쟁을 줄이기 위해 기록 중심으로 설계되어 있습니다.

| Record | Purpose |
|---|---|
| `first_drafted_at` | 기여자가 아이디어 작성을 시작한 서버 시각 보존 |
| `ViewLog` | 원작자가 PR을 열람한 사실 기록 |
| `RejectReason` | 거절 사유와 변경 이력 보존 |
| `AuditLog` | 제출, 열람, 수락, 수정 요청, 거절, 병합, 등급 조정 기록 |
| `Merge` | 공식 반영, 크레딧, 외부 인용 URL 보존 |

## Docs

| Document | Link |
|---|---|
| API specs | [`docs/api`](docs/api) |
| DB specs | [`docs/db`](docs/db) |
| Page/API mapping | [`docs/pages`](docs/pages) |
| User scenarios | [`docs/user-scenarios.md`](docs/user-scenarios.md) |
| Information architecture | [`docs/ia.md`](docs/ia.md) |

## Development Notes

- `.env`는 Git에 올리지 않습니다. `.env.example`만 공유합니다.
- DB 삭제 대신 상태값과 로그로 이력을 보존하는 방향을 우선합니다.
- Stats는 MVP에서 테이블로 저장하지 않고 쿼리로 계산합니다.
- 이미지 업로드는 MVP 범위 밖입니다. Repository thumbnail은 URL 문자열만 저장합니다.
- OAuth, 결제, 계약서, 수익 분배, 블록체인 timestamp는 V2 이후 범위입니다.

---

<p align="center">
  서랍 turns creative ideas into reviewable, creditable contributions.
</p>
