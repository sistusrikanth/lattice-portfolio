from datetime import datetime
from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    title: str
    slug: str | None = None
    summary: str = ""
    content: str = ""
    category: str = "papers"
    tags: str = ""
    read_time_min: int = 5
    featured: bool = False
    published: bool = True


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    content: str | None = None
    category: str | None = None
    tags: str | None = None
    read_time_min: int | None = None
    featured: bool | None = None
    published: bool | None = None


class ArticleOut(ArticleBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PhotoLinkBase(BaseModel):
    title: str = ""
    instagram_url: str
    category: str = "street"
    sort_order: int = 0


class PhotoLinkCreate(PhotoLinkBase):
    pass


class PhotoLinkOut(PhotoLinkBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    url: str
    status: str
    tech_tags: str
    icon_color: str
    sort_order: int

    model_config = {"from_attributes": True}


class StartupIdeaOut(BaseModel):
    id: int
    title: str
    description: str
    contact_url: str
    sort_order: int

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    password: str


class DayEntryBase(BaseModel):
    entry_date: str
    personal: str = ""
    professional: str = ""


class DayEntryCreate(DayEntryBase):
    pass


class DayEntryOut(DayEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IdentityCardBase(BaseModel):
    category: str
    content: str = ""


class IdentityCardUpdate(BaseModel):
    content: str


class IdentityCardOut(IdentityCardBase):
    id: int
    updated_at: datetime

    model_config = {"from_attributes": True}
