from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

async_session = sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


async def get_session():
    async with async_session() as session:
        yield session
