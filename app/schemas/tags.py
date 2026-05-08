from pydantic import BaseModel


class TagInfo(BaseModel):
    id: int
    name: str


class TagListResponse(BaseModel):
    tags: list[TagInfo]


class PopularTagInfo(BaseModel):
    id: int
    name: str
    repository_count: int


class PopularTagListResponse(BaseModel):
    tags: list[PopularTagInfo]
