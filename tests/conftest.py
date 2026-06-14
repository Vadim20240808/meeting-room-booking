import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import get_session
from app.models import Base, User, Room, Slot
from app.auth import get_password_hash
from datetime import time

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_session():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create test data: admin, user, rooms, slots
    async with TestSessionLocal() as session:
        # Users
        admin = User(username="admin", hashed_password=get_password_hash("adminpass"), is_admin=True)
        user = User(username="user", hashed_password=get_password_hash("userpass"), is_admin=False)
        session.add_all([admin, user])
        await session.commit()

        # Rooms
        room1 = Room(name="Переговорная 1")
        room2 = Room(name="Переговорная 2")
        session.add_all([room1, room2])
        await session.commit()

        # Slots for room1
        slot1 = Slot(room_id=room1.id, start_time=time(9,0), end_time=time(11,0))
        slot2 = Slot(room_id=room1.id, start_time=time(13,0), end_time=time(16,0))
        # Slots for room2
        slot3 = Slot(room_id=room2.id, start_time=time(10,0), end_time=time(12,0))
        session.add_all([slot1, slot2, slot3])
        await session.commit()

    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def user_token(client):
    response = await client.post("/auth/login", json={"username": "user", "password": "userpass"})
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def admin_token(client):
    response = await client.post("/auth/login", json={"username": "admin", "password": "adminpass"})
    return response.json()["access_token"]