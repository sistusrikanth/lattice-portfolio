from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    summary = Column(Text, default="")
    content = Column(Text, default="")
    category = Column(String(50), default="papers")  # papers, systems, notes
    tags = Column(String(500), default="")
    read_time_min = Column(Integer, default=5)
    featured = Column(Boolean, default=False)
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class PhotoLink(Base):
    __tablename__ = "photo_links"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), default="")
    instagram_url = Column(String(1000), nullable=False)
    category = Column(String(50), default="street")  # street, landscape, architecture, portrait
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    url = Column(String(1000), default="")
    status = Column(String(20), default="wip")  # live, wip
    tech_tags = Column(String(500), default="")
    icon_color = Column(String(20), default="#6366f1")
    sort_order = Column(Integer, default=0)


class StartupIdea(Base):
    __tablename__ = "startup_ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    contact_url = Column(String(1000), default="")
    sort_order = Column(Integer, default=0)


class DayEntry(Base):
    __tablename__ = "day_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(String(10), unique=True, nullable=False, index=True)  # YYYY-MM-DD
    personal = Column(Text, default="")
    professional = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class IdentityCard(Base):
    __tablename__ = "identity_cards"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, nullable=False, index=True)
    content = Column(Text, default="")
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
