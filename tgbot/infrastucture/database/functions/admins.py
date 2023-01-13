from typing import Coroutine, Any

from sqlalchemy import select, insert, func, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from tgbot.infrastucture.database.models.admins import Admins


async def get_admin(session: AsyncSession, **kwargs) -> Coroutine[Any, Any, Any]:
    statement = select(Admins).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def add_admin(session: AsyncSession, telegram_id):
    statement = insert(
        Admins
    ).values(
        telegram_id=telegram_id
    )

    await session.execute(statement)
    await session.commit()


async def delete_admin(session: AsyncSession, telegram_id):
    statement = delete(
        Admins
    ).where(
        Admins.telegram_id == telegram_id
    )

    await session.execute(statement)
    await session.commit()


async def get_count_admins(session: AsyncSession, *clauses):
    statement = select(
        func.count(Admins.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def get_all_admins(session: AsyncSession):
    statement = select(Admins)
    result: AsyncResult = await session.scalars(statement)
    return result.all()
