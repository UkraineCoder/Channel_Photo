import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.infrastucture.database.functions.admins import add_admin, get_admin, delete_admin, get_count_admins, \
    get_all_admins
from tgbot.misc.states import AdminNew, AdminDelete


async def admin_new(message: Message):
    await message.answer("Enter new admin id")
    await AdminNew.Id.set()


async def admin_new_save(message: Message, state: FSMContext, session):
    admin_id = await get_admin(session, telegram_id=int(message.text))

    if admin_id:
        await message.answer("❌ Admin already exists")
    else:
        await add_admin(session, telegram_id=int(message.text))
        await message.answer("✅ Admin added")

    await state.finish()


async def admin_delete(message: Message, session):
    count_admins = await get_count_admins(session)

    if count_admins == 1:
        await message.answer("❌ You can't delete the last admin")
        return

    await message.answer("Enter which id you want to deleted")
    await AdminDelete.Id.set()


async def admin_delete_save(message: Message, state: FSMContext, session):
    admin_id = await get_admin(session, telegram_id=int(message.text))

    if admin_id:
        await delete_admin(session, telegram_id=int(message.text))
        await message.answer("✅ Admin deleted")
    else:
        await message.answer("❌ Admin not found")

    await state.finish()


async def admin_validate(message: Message):
    await message.answer("❌ Id must be a number")


async def admin_list(message: Message, session):
    admins = await get_all_admins(session)

    await message.answer(f"Admins: {', '.join([str(admin.telegram_id) for admin in admins])}")


def register_admin_add(dp: Dispatcher):
    dp.register_message_handler(admin_new, commands=["admin_new"], is_admin=True)
    dp.register_message_handler(admin_new_save, regexp=re.compile(r'^\d+$'), state=AdminNew.Id)

    dp.register_message_handler(admin_delete, commands=["admin_delete"], is_admin=True)
    dp.register_message_handler(admin_delete_save, regexp=re.compile(r'^\d+$'), state=AdminDelete.Id)

    dp.register_message_handler(admin_validate, state=[AdminNew.Id, AdminDelete.Id])

    dp.register_message_handler(admin_list, commands=["admin_list"], is_admin=True)
