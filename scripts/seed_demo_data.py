from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.db import base as _models  # noqa: E402,F401
from app.db.session import SessionLocal  # noqa: E402
from app.models.repository import (  # noqa: E402
    RecruitingArea,
    RepoCharacter,
    RepoForbidden,
    RepoRegion,
    RepoRule,
    Repository,
    RepositoryTag,
    Tag,
)
from app.models.user import User  # noqa: E402
from app.services.auth import hash_password  # noqa: E402


PASSWORD = "Demo1234!"


USERS = [
    {
        "username": "demo_author",
        "email": "demo.author@worldbuild-demo.com",
        "avatar_url": "https://api.dicebear.com/8.x/adventurer/svg?seed=demo_author",
        "bio": "시연용 원작자 계정입니다. 별빛 기록관 세계관을 관리합니다.",
    },
    {
        "username": "demo_contributor",
        "email": "demo.contributor@worldbuild-demo.com",
        "avatar_url": "https://api.dicebear.com/8.x/adventurer/svg?seed=demo_contributor",
        "bio": "시연용 컨트리뷰터 계정입니다. 다른 세계관에 PR을 보냅니다.",
    },
    {
        "username": "demo_archivist",
        "email": "demo.archivist@worldbuild-demo.com",
        "avatar_url": "https://api.dicebear.com/8.x/adventurer/svg?seed=demo_archivist",
        "bio": "고대 문서와 잊힌 왕조를 다루는 더미 원작자입니다.",
    },
    {
        "username": "demo_neon",
        "email": "demo.neon@worldbuild-demo.com",
        "avatar_url": "https://api.dicebear.com/8.x/adventurer/svg?seed=demo_neon",
        "bio": "도시 판타지와 사이버 요괴물을 좋아하는 더미 원작자입니다.",
    },
    {
        "username": "demo_orbit",
        "email": "demo.orbit@worldbuild-demo.com",
        "avatar_url": "https://api.dicebear.com/8.x/adventurer/svg?seed=demo_orbit",
        "bio": "우주 상인과 궤도 도시를 만드는 더미 원작자입니다.",
    },
]


REPOS = [
    {
        "slug": "demo-starlight-archive",
        "author": "demo_author",
        "title": "별빛 기록관",
        "description": "사라진 별들의 기억을 보관하는 도시 판타지 세계관",
        "thumbnail_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80",
        "external_links": [{"label": "시연 가이드", "url": "https://example.com/worldbuild-demo"}],
        "readme_overview": (
            "별빛 기록관은 사람들의 기억에서 사라진 별, 도시, 인물을 문서와 유물로 보관하는 "
            "비밀 기관입니다. 기록관의 사서들은 별가루 잉크로 사건을 봉인하고, 컨트리뷰터는 "
            "새로운 캐릭터와 에피소드를 제안할 수 있습니다."
        ),
        "contribution_guideline": (
            "기록관의 규칙을 해치지 않는 캐릭터, 사건, 장소 제안을 환영합니다. 제안에는 "
            "인물의 목표, 기록관과의 관계, 기존 규칙과 충돌하지 않는 이유를 포함해주세요."
        ),
        "tags": ["판타지", "기록관", "별", "PR시연"],
        "characters": [
            {"name": "하린", "content": "별빛 기록관의 신입 사서. 사라진 별의 이름을 들을 수 있다."},
            {"name": "이든", "content": "기록관의 야간 관리자. 금지된 서고의 열쇠를 보관한다."},
        ],
        "regions": [
            {"name": "중앙 서고", "content": "도시 지하에 숨겨진 거대한 원형 서고."},
            {"name": "잊힌 별의 관측실", "content": "기록에서 사라진 별빛만 보이는 돔형 관측실."},
        ],
        "rules": [
            {
                "name": "기억 보존 규칙",
                "content": "기록관에 봉인된 기억은 원작자의 승인 없이는 현실에 되돌릴 수 없다.",
            },
            {"name": "별가루 잉크", "content": "별가루 잉크로 적힌 문장은 거짓을 담을 수 없다."},
        ],
        "forbidden": [
            {
                "name": "전지전능한 존재",
                "content": "모든 기록을 즉시 수정하거나 삭제할 수 있는 절대자는 금지됩니다.",
            },
            {
                "name": "기록관 파괴",
                "content": "세계관의 핵심 무대인 기록관 자체를 완전히 파괴하는 설정은 금지됩니다.",
            },
        ],
        "recruiting_areas": ["character_add", "event_episode", "worldbuilding"],
    },
    {
        "slug": "demo-moonlit-court",
        "author": "demo_archivist",
        "title": "월영 궁정",
        "description": "달빛으로 봉인된 왕가와 그림자 기사단의 궁정 판타지",
        "thumbnail_url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=1200&q=80",
        "external_links": [],
        "readme_overview": "달이 붉게 뜨는 밤마다 궁정의 비밀 재판이 열리는 고전 판타지 세계입니다.",
        "contribution_guideline": "귀족 가문, 궁정 암투, 기사단 에피소드 제안을 받습니다.",
        "tags": ["궁정", "판타지", "달"],
        "characters": [{"name": "세레나", "content": "월영 왕국의 섭정. 달의 인장을 지녔다."}],
        "regions": [{"name": "흑월 회랑", "content": "궁정의 그림자 재판이 열리는 긴 복도."}],
        "rules": [{"name": "달의 맹세", "content": "달빛 아래 맺은 맹세는 깨면 그림자를 잃는다."}],
        "forbidden": [{"name": "왕가 즉시 몰락", "content": "왕국 구조를 한 번에 무너뜨리는 설정은 지양합니다."}],
        "recruiting_areas": ["relationship", "event_episode"],
    },
    {
        "slug": "demo-neon-gumiho-bureau",
        "author": "demo_neon",
        "title": "네온 구미호 수사국",
        "description": "요괴와 인간이 공존하는 미래 도시의 초상수사물",
        "thumbnail_url": "https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=1200&q=80",
        "external_links": [],
        "readme_overview": "네온 간판 아래에서 요괴 범죄를 추적하는 특수 수사국 이야기입니다.",
        "contribution_guideline": "사건, 요괴 능력, 수사 파트너 캐릭터 제안을 환영합니다.",
        "tags": ["도시판타지", "수사", "요괴"],
        "characters": [{"name": "류서아", "content": "구미호 혈통의 프로파일러. 거짓말의 냄새를 맡는다."}],
        "regions": [{"name": "홍련 7번가", "content": "요괴 밀거래가 자주 발생하는 야시장 거리."}],
        "rules": [{"name": "정체 은폐법", "content": "요괴는 인간 사회에서 정체를 공개하면 보호권을 잃는다."}],
        "forbidden": [{"name": "무제한 변신", "content": "능력에는 반드시 대가나 제한이 있어야 합니다."}],
        "recruiting_areas": ["item_ability_rule", "event_episode", "character_add"],
    },
    {
        "slug": "demo-orbit-market",
        "author": "demo_orbit",
        "title": "궤도 시장 23번 구역",
        "description": "행성 궤도를 도는 거대 시장 정거장의 SF 군상극",
        "thumbnail_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1200&q=80",
        "external_links": [],
        "readme_overview": "우주 상인, 밀수꾼, 외교관이 뒤섞이는 궤도 시장의 이야기입니다.",
        "contribution_guideline": "상점, 외계 종족, 거래 규칙, 작은 사건 제안을 받습니다.",
        "tags": ["SF", "우주", "시장"],
        "characters": [{"name": "모라", "content": "23번 구역의 중재자. 어떤 거래도 기억한다."}],
        "regions": [{"name": "무중력 경매장", "content": "물건과 사람이 함께 떠다니는 경매 구역."}],
        "rules": [{"name": "거래 보증", "content": "시장의 공식 거래는 중재자 기록에 남아야 효력을 가진다."}],
        "forbidden": [{"name": "지구 중심 설정", "content": "이 세계의 중심은 궤도 시장이며 지구는 배경으로만 다룹니다."}],
        "recruiting_areas": ["region", "item_ability_rule", "other"],
    },
]


def upsert_user(db: Session, data: dict) -> User:
    password_hash = hash_password(PASSWORD)
    user = db.scalar(select(User).where(User.username == data["username"]))
    if user is None:
        user = User(username=data["username"], email=data["email"].lower(), password_hash=password_hash)
        db.add(user)
        db.flush()

    user.email = data["email"].lower()
    user.password_hash = password_hash
    user.avatar_url = data["avatar_url"]
    user.bio = data["bio"]
    return user


def get_or_create_tag_id(db: Session, name: str) -> int:
    cleaned = name.strip()
    tag = db.scalar(select(Tag).where(func.lower(Tag.name) == cleaned.lower()))
    if tag is None:
        tag = Tag(name=cleaned)
        db.add(tag)
        db.flush()
    return tag.id


def replace_repo_collections(db: Session, repo: Repository, spec: dict) -> None:
    for model in (RepositoryTag, RepoCharacter, RepoRegion, RepoRule, RepoForbidden, RecruitingArea):
        db.execute(delete(model).where(model.repository_id == repo.id))
    db.flush()

    tag_ids = []
    seen_tag_ids = set()
    for tag_name in spec["tags"]:
        tag_id = get_or_create_tag_id(db, tag_name)
        if tag_id not in seen_tag_ids:
            seen_tag_ids.add(tag_id)
            tag_ids.append(tag_id)

    for tag_id in tag_ids:
        db.add(RepositoryTag(repository_id=repo.id, tag_id=tag_id))
    for index, item in enumerate(spec["characters"]):
        db.add(RepoCharacter(repository_id=repo.id, name=item["name"], content=item["content"], order_index=index))
    for index, item in enumerate(spec["regions"]):
        db.add(RepoRegion(repository_id=repo.id, name=item["name"], content=item["content"], order_index=index))
    for index, item in enumerate(spec["rules"]):
        db.add(RepoRule(repository_id=repo.id, name=item["name"], content=item["content"], order_index=index))
    for index, item in enumerate(spec["forbidden"]):
        db.add(RepoForbidden(repository_id=repo.id, name=item["name"], content=item["content"], order_index=index))
    for index, area in enumerate(spec["recruiting_areas"]):
        db.add(RecruitingArea(repository_id=repo.id, name=area, content="", order_index=index, is_active=True))


def upsert_repo(db: Session, spec: dict, users: dict[str, User]) -> Repository:
    repo = db.scalar(select(Repository).where(Repository.slug == spec["slug"]))
    if repo is None:
        repo = Repository(slug=spec["slug"], author_id=users[spec["author"]].id, title=spec["title"])
        db.add(repo)
        db.flush()

    repo.author_id = users[spec["author"]].id
    repo.title = spec["title"]
    repo.description = spec["description"]
    repo.thumbnail_url = spec["thumbnail_url"]
    repo.external_links = spec["external_links"]
    repo.readme_overview = spec["readme_overview"]
    repo.contribution_guideline = spec["contribution_guideline"]
    replace_repo_collections(db, repo, spec)
    db.flush()
    return repo


def main() -> None:
    db = SessionLocal()
    try:
        users = {data["username"]: upsert_user(db, data) for data in USERS}
        repos = [upsert_repo(db, spec, users) for spec in REPOS]
        db.commit()
        user_summaries = [
            (username, users[username].email, users[username].id)
            for username in ("demo_author", "demo_contributor")
        ]
        repo_summaries = [
            (repo.id, repo.slug, repo.title, repo.author_id)
            for repo in repos
        ]
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Seed complete")
    print(f"Password for all seed accounts: {PASSWORD}")
    for username, email, user_id in user_summaries:
        print(f"User: {username} / {email} / id={user_id}")
    for repo_id, slug, title, author_id in repo_summaries:
        print(f"Repo: id={repo_id} slug={slug} title={title} author_id={author_id}")


if __name__ == "__main__":
    main()
