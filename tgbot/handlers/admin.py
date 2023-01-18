import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.infrastucture.database.functions.channel_photo import add_channel_photo
from tgbot.misc.states import AdminTotalTime


async def admin_start(message: Message):
    await message.answer("Hi send photo")


async def admin_photo(message: types.Message, session):
    file_id = message.photo[-1].file_id

    photo = await add_channel_photo(session, file_id)

    await message.reply(f"✅ Photo added\n {photo.photo_id}")


async def edit_total_time(message: types.Message):
    await message.answer("Send time in minutes")

    await AdminTotalTime.Time.set()


async def set_time(message: types.Message, state: FSMContext, scheduler):
    time = message.text
    await state.update_data(time=time)

    scheduler.reschedule_job('send_message_to_channel', trigger='interval', minutes=int(time))

    await message.answer("✅ Time changed")

    await state.finish()


async def set_time_error(message: types.Message):
    await message.answer("❌ Time must be in minutes")


async def admin_help(message: types.Message):
    await message.answer("/start\n"
                         "/admin_new - add new admin\n"
                         "/admin_delete - delete admin\n"
                         "/admin_list - list of admins\n"
                         "/edit_time - also the same\n"
                         "/edit_total_time - total time\n"
                         "/info_schedule - information about scheduled pictures\n"
                         "/info_time - information about unscheduled pictures, those that come every 15 minutes\n"
                         "/delete_time - deletes everything")


async def cancel_admin(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text("❌ Cancelled")
    await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_admin, text="admin_cancel", state="*")
    dp.register_message_handler(admin_start, commands=["start"], is_admin=True)
    dp.register_message_handler(admin_help, commands=["help"], is_admin=True)
    dp.register_message_handler(admin_photo, content_types=types.ContentType.PHOTO, is_admin=True)
    dp.register_message_handler(edit_total_time, commands=["edit_total_time"], is_admin=True)
    dp.register_message_handler(set_time, regexp=re.compile(r"^[1-9]\d*$"), state=AdminTotalTime.Time)
    dp.register_message_handler(set_time_error, state=AdminTotalTime.Time)


