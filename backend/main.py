import os
import re
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from auth import create_access_token, require_admin, verify_password
from database import Base, SessionLocal, engine, get_db
from models import Article, DayEntry, IdentityCard, PhotoLink, Project, StartupIdea
from schemas import (
    ArticleCreate,
    ArticleOut,
    ArticleUpdate,
    DayEntryCreate,
    DayEntryOut,
    IdentityCardOut,
    IdentityCardUpdate,
    LoginRequest,
    PhotoLinkCreate,
    PhotoLinkOut,
    ProjectOut,
    StartupIdeaOut,
    Token,
)

STATIC_DIR = Path(__file__).parent / "static"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def seed_data(db: Session):
    if db.query(Article).count() > 0:
        return

    articles = [
        Article(
            title="Attention is a weighted lookup",
            slug="attention-is-a-weighted-lookup",
            summary="Transformers reduce to one operation: weighted retrieval over a key-value store. Everything else is bookkeeping.",
            content="""# Attention is a weighted lookup

Transformers look complicated until you strip away the notation. At the core, **attention is just a weighted lookup** over a key-value store.

## The setup

You have three matrices: **Q** (queries), **K** (keys), and **V** (values). For each query vector, you:

1. Compute similarity scores against every key
2. Softmax those scores into weights
3. Return a weighted sum of value vectors

That's it. The rest — multi-head attention, positional encodings, layer norms — is engineering around this primitive.

## Why it works

Language is full of long-range dependencies. A pronoun ten words back needs to bind to a noun. Attention gives every token direct access to every other token in one hop, instead of squeezing context through a fixed-size bottleneck.

## The cost

Quadratic memory in sequence length. At 8k tokens you're fine. At 128k you need KV-cache tricks, sparse patterns, or ring attention.

---

*This is a seed article. Edit or replace it from the admin panel.*
""",
            category="papers",
            tags="transformers",
            read_time_min=14,
            featured=True,
        ),
        Article(
            title="Designing a feature store",
            slug="designing-a-feature-store",
            summary="Online vs offline features, point-in-time correctness, and why most teams get the serving path wrong.",
            content="# Designing a feature store\n\nSeed content — replace from admin.",
            category="systems",
            tags="data,serving",
            read_time_min=11,
        ),
        Article(
            title="KV-cache eviction heuristics",
            slug="kv-cache-eviction",
            summary="Quick notes on what to drop when context windows outgrow GPU memory.",
            content="# KV-cache eviction\n\nSeed content — replace from admin.",
            category="notes",
            tags="gpu,inference",
            read_time_min=6,
        ),
    ]
    db.add_all(articles)

    photos = [
        PhotoLink(title="Lisbon morning", instagram_url="https://www.instagram.com/", category="street", sort_order=1),
        PhotoLink(title="Coast light", instagram_url="https://www.instagram.com/", category="landscape", sort_order=2),
        PhotoLink(title="Concrete curves", instagram_url="https://www.instagram.com/", category="architecture", sort_order=3),
    ]
    db.add_all(photos)

    projects = [
        Project(
            title="lattice",
            description="A personal publishing system — writing, systems, photography in one grid.",
            url="#",
            status="live",
            tech_tags="ts,react,python",
            icon_color="#6366f1",
            sort_order=1,
        ),
        Project(
            title="ring-buffer",
            description="Zero-copy ring buffer for streaming inference pipelines.",
            url="#",
            status="wip",
            tech_tags="rust,wasm",
            icon_color="#8b5cf6",
            sort_order=2,
        ),
        Project(
            title="paper-lens",
            description="Upload a PDF, get a component diagram and a plain-English walkthrough.",
            url="#",
            status="wip",
            tech_tags="python,pdf.js",
            icon_color="#3b82f6",
            sort_order=3,
        ),
    ]
    db.add_all(projects)

    ideas = [
        StartupIdea(
            title="Diff for ML configs",
            description="Git-style diffs for training configs — see exactly what changed between runs and why loss moved.",
            contact_url="mailto:hello@example.com",
            sort_order=1,
        ),
        StartupIdea(
            title="On-call for models",
            description="PagerDuty, but the alerts are drift scores and latency regressions, not disk space.",
            contact_url="mailto:hello@example.com",
            sort_order=2,
        ),
        StartupIdea(
            title="Notebook CI",
            description="Run notebooks as tests on every PR. Catch stale outputs before they ship.",
            contact_url="mailto:hello@example.com",
            sort_order=3,
        ),
    ]
    db.add_all(ideas)
    db.commit()


def _seed_identity(db: Session):
    if db.query(IdentityCard).count() > 0:
        return
    identity_seed = [
        ("who_i_am", "I break complex systems down to their essence. Reader, builder, photographer — based in Lisbon."),
        ("what_i_do", "I read research papers and rebuild them from first principles. I design ML systems in the open. I shoot cities and light between commits."),
        ("what_i_care_about", "Clarity over cleverness. Systems that survive failure. Ideas that outlive the hype cycle. Showing up every day."),
        ("writing", "Research papers, taken apart and rebuilt from their core components — the wiring made visible."),
        ("systems", "The ML systems everyone leans on, drawn out from first principles — trade-offs left in."),
        ("photography", "A working portfolio. Film when there's time, digital when there isn't."),
        ("projects", "Things I'm building and startup ideas I can't stop thinking about."),
    ]
    for category, content in identity_seed:
        db.add(IdentityCard(category=category, content=content))
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
        _seed_identity(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Lattice Portfolio API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth ---

@app.post("/api/auth/login", response_model=Token)
def login(body: LoginRequest):
    if not verify_password(body.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return Token(access_token=create_access_token())


# --- Articles (public) ---

@app.get("/api/articles", response_model=list[ArticleOut])
def list_articles(
    category: str | None = None,
    featured: bool | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Article).filter(Article.published == True)
    if category and category != "all":
        q = q.filter(Article.category == category)
    if featured is not None:
        q = q.filter(Article.featured == featured)
    return q.order_by(Article.created_at.desc()).all()


@app.get("/api/articles/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug, Article.published == True).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# --- Articles (admin) ---

@app.post("/api/admin/articles", response_model=ArticleOut)
def create_article(body: ArticleCreate, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    slug = body.slug or slugify(body.title)
    if db.query(Article).filter(Article.slug == slug).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    article = Article(**body.model_dump(exclude={"slug"}), slug=slug)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@app.put("/api/admin/articles/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    body: ArticleUpdate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        if key == "slug" and value:
            existing = db.query(Article).filter(Article.slug == value, Article.id != article_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Slug already exists")
        setattr(article, key, value)
    db.commit()
    db.refresh(article)
    return article


@app.delete("/api/admin/articles/{article_id}")
def delete_article(article_id: int, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/articles", response_model=list[ArticleOut])
def admin_list_articles(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.created_at.desc()).all()


# --- Photography ---

@app.get("/api/photos", response_model=list[PhotoLinkOut])
def list_photos(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(PhotoLink)
    if category and category != "all":
        q = q.filter(PhotoLink.category == category)
    return q.order_by(PhotoLink.sort_order, PhotoLink.created_at.desc()).all()


@app.post("/api/admin/photos", response_model=PhotoLinkOut)
def create_photo(body: PhotoLinkCreate, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    photo = PhotoLink(**body.model_dump())
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@app.delete("/api/admin/photos/{photo_id}")
def delete_photo(photo_id: int, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    photo = db.query(PhotoLink).filter(PhotoLink.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(photo)
    db.commit()
    return {"ok": True}


# --- Projects ---

@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.sort_order).all()


@app.get("/api/ideas", response_model=list[StartupIdeaOut])
def list_ideas(db: Session = Depends(get_db)):
    return db.query(StartupIdea).order_by(StartupIdea.sort_order).all()


# --- Private: day tracker (admin only) ---

@app.get("/api/admin/days", response_model=list[DayEntryOut])
def list_day_entries(
    limit: int = Query(60, le=365),
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(DayEntry).order_by(DayEntry.entry_date.desc()).limit(limit).all()


@app.get("/api/admin/days/{entry_date}", response_model=DayEntryOut)
def get_day_entry(entry_date: str, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    entry = db.query(DayEntry).filter(DayEntry.entry_date == entry_date).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.put("/api/admin/days/{entry_date}", response_model=DayEntryOut)
def upsert_day_entry(
    entry_date: str,
    body: DayEntryCreate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    entry = db.query(DayEntry).filter(DayEntry.entry_date == entry_date).first()
    if entry:
        entry.personal = body.personal
        entry.professional = body.professional
    else:
        entry = DayEntry(entry_date=entry_date, personal=body.personal, professional=body.professional)
        db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.delete("/api/admin/days/{entry_date}")
def delete_day_entry(entry_date: str, _: bool = Depends(require_admin), db: Session = Depends(get_db)):
    entry = db.query(DayEntry).filter(DayEntry.entry_date == entry_date).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}


# --- Private: identity cards (admin only) ---

IDENTITY_ORDER = [
    "who_i_am", "what_i_do", "what_i_care_about",
    "writing", "systems", "photography", "projects",
]


@app.get("/api/admin/identity", response_model=list[IdentityCardOut])
def list_identity_cards(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    cards = db.query(IdentityCard).all()
    order = {cat: i for i, cat in enumerate(IDENTITY_ORDER)}
    return sorted(cards, key=lambda c: order.get(c.category, 99))


@app.put("/api/admin/identity/{category}", response_model=IdentityCardOut)
def update_identity_card(
    category: str,
    body: IdentityCardUpdate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    card = db.query(IdentityCard).filter(IdentityCard.category == category).first()
    if not card:
        card = IdentityCard(category=category, content=body.content)
        db.add(card)
    else:
        card.content = body.content
    db.commit()
    db.refresh(card)
    return card


# --- Site config ---

@app.get("/api/config")
def site_config():
    return {
        "name": os.environ.get("SITE_NAME", "kiran rao"),
        "tagline": os.environ.get("SITE_TAGLINE", "writing, systems & photography"),
        "location": os.environ.get("SITE_LOCATION", "Lisbon"),
        "github": os.environ.get("SITE_GITHUB", "https://github.com/sistusrikanth"),
        "twitter": os.environ.get("SITE_TWITTER", ""),
        "email": os.environ.get("SITE_EMAIL", ""),
        "now_text": os.environ.get(
            "SITE_NOW_TEXT",
            "Writing up a piece on KV-cache eviction. Shooting a roll of Portra in Lisbon.",
        ),
    }


# --- Static files (production) ---

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
