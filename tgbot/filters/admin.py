import typing
from aiogram.dispatcher.filters import BoundFilter
from tgbot.infrastucture.database.functions.admins import get_admin


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False

        session_pool = obj.bot.get('session_pool')

        async with session_pool() as session:
            admin = await get_admin(session, telegram_id=obj.from_user.id)
            return bool(admin)

