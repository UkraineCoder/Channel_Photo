from typing import Coroutine, Any

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from tgbot.infrastucture.database.models.channel_photo import ChannelPhoto


async def add_channel_photo(session: AsyncSession, file_id):
    insert_stmt = select(
        ChannelPhoto
    ).from_statement(
        insert(
            ChannelPhoto
        ).values(
            file_id=file_id
        ).returning(ChannelPhoto).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    await session.commit()
    return result.first()


async def get_channel_photo(session: AsyncSession, **kwargs) -> Coroutine[Any, Any, Any]:
    statement = select(ChannelPhoto).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_photo(session: AsyncSession) -> Coroutine[Any, Any, Any]:
    statement = select(ChannelPhoto)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_all_channel_photo(session: AsyncSession) -> Coroutine[Any, Any, Any]:
    statement = select(ChannelPhoto)
    result: AsyncResult = await session.scalars(statement)
    return result.all()


async def delete_channel_photo(session: AsyncSession, photo_id):
    statement = delete(
        ChannelPhoto
    ).where(
        ChannelPhoto.photo_id == photo_id
    )

    await session.execute(statement)
    await session.commit()





