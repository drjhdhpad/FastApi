from fastapi import FastAPI

from app.database import engine
from app.db_migrations import run_migrations
from app.models import Base  # noqa: F401 - importing registers all ORM models
from app.api.v1 import addresses, ads, categories, messages, search, users

Base.metadata.create_all(bind=engine)
run_migrations(engine)

app = FastAPI(title="Marketplace API")
app.include_router(users.router)
app.include_router(ads.router)
app.include_router(ads.legacy_stats_router)
app.include_router(categories.router)
app.include_router(search.router)
app.include_router(addresses.router)
app.include_router(messages.router)


# uvicorn app.main:app --reload