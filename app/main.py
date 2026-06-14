from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select  # добавьте импорт
from app.database import engine, async_session_maker
from app.models import Base, User
from app.security import get_password_hash
from app.routers import auth_router, rooms_router, bookings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # === Создаём тестовых пользователей ===
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        if not result.scalars().all():
            admin = User(
                username="admin",
                hashed_password=get_password_hash("adminpass"),
                is_admin=True
            )
            user = User(
                username="user",
                hashed_password=get_password_hash("userpass"),
                is_admin=False
            )
            session.add_all([admin, user])
            await session.commit()

    yield
    await engine.dispose()

app = FastAPI(title="Meeting Room Booking", lifespan=lifespan)

app.include_router(auth_router.router)
app.include_router(rooms_router.router)
app.include_router(bookings_router.router)

@app.get("/")
async def root():
    return {"message": "Booking service"}