import datetime
import re

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.config import Config
from tgbot.filters.time import HourFilter, MinuteFilter
from tgbot.handlers.aiogram_calendar.simple_calendar import SimpleCalendar, calendar_callback
from tgbot.infrastucture.database.functions.channel_photo import get_channel_photo, delete_channel_photo
from tgbot.inline.buttons import cancel_button
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import AdminEditTime


async def edit_time(message: Message, state: FSMContext):
    msg = await message.answer('Enter the ID of the image you want to edit', reply_markup=cancel_button())

    await state.update_data(msg=msg.message_id)

    await AdminEditTime.Id.set()


async def save_data(message: Message, state: FSMContext, file_id):
    await message.answer("🗓 Please select a date", reply_markup=await SimpleCalendar().start_calendar())

    await state.update_data(photo_id=message.text, file_id=file_id)

    await AdminEditTime.Choose_Calendar.set()


async def get_photo_id(message: Message, state: FSMContext, session, scheduler):
    await delete_markup(message, state)

    photo = await get_channel_photo(session, photo_id=int(message.text))

    for job in scheduler.get_jobs():
        if job.id == message.text:
            file_id = job.kwargs['file_id']
            await save_data(message, state, file_id)
            return

    if photo:
        await save_data(message, state, photo.file_id)
    else:
        msg = await message.answer('Error id not found', reply_markup=cancel_button())
        await state.update_data(msg=msg.message_id)


async def get_photo_id_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer("❌ Error\n"
                               "Send a number and no extra characters", reply_markup=cancel_button())
    await state.update_data(msg=msg.message_id)


async def send_calendar_true(call, state, date_calendar):
    await call.message.edit_text("⏰ What hour do you want to send the photo?", reply_markup=cancel_button())

    await state.update_data(date=str(date_calendar), msg=call.message.message_id)

    await AdminEditTime.Choose_Hour.set()


async def send_calendar(call: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date_calendar = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        date = str(date_calendar).split()[0]
        date_now = str(datetime.datetime.now()).split()[0]

        my_dt = datetime.datetime.strptime(str(date), '%Y-%m-%d')
        date_now_sort = datetime.datetime.strptime(str(date_now), '%Y-%m-%d')

        if my_dt == date_now_sort:
            await send_calendar_true(call, state, date_calendar)
        elif my_dt >= datetime.datetime.now():
            await send_calendar_true(call, state, date_calendar)
        else:
            await call.answer("❗️ You can't send a photo to the past", show_alert=True)


async def send_calendar_text(message: Message):
    await message.answer("❗️ Choose the time in the calendar")


async def send_calendar_hour(message: Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer("⏰ What minutes do you want to send the photo?", reply_markup=cancel_button())

    await state.update_data(hour=message.text, msg=msg.message_id)

    await AdminEditTime.Choose_Minute.set()


async def send_calendar_hour_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer("❌ Error\n"
                               "Send a number between 0-23 and no extra characters", reply_markup=cancel_button())

    await state.update_data(msg=msg.message_id)


async def photo_job(file_id, bot: Bot, config: Config):
    await bot.send_photo(chat_id=config.tg_bot.channel_id, photo=file_id)


async def send_calendar_minute(message: types.Message, state: FSMContext, session, scheduler):
    await delete_markup(message, state)

    data = await state.get_data()

    date = data['date'].split()
    hour = int(data['hour'])
    minute = int(message.text)

    date_sort = date[0].split("-")
    year = int(date_sort[0])
    month = int(date_sort[1])
    day = int(date_sort[2])

    if datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute) <= datetime.datetime.now():
        msg = await message.answer("❗️ You can't send a photo to the past", reply_markup=cancel_button())
        await state.update_data(msg=msg.message_id)
        return

    photo_id = data['photo_id']
    file_id = data['file_id']

    photo = await get_channel_photo(session, photo_id=int(photo_id))

    try:
        for job in scheduler.get_jobs():
            if job.id == str(photo_id):
                scheduler.reschedule_job(
                    str(photo_id),
                    trigger='date',
                    timezone='Europe/Kiev',
                    run_date=datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                )

                await message.answer("✅ Photo successfully updated in the schedule")

        if photo:
            scheduler.add_job(
                photo_job,
                'date',
                run_date=datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute),
                timezone='Europe/Kiev',
                kwargs=dict(file_id=file_id),
                id=str(photo_id)
            )

            await delete_channel_photo(session, int(photo_id))

            await message.answer("✅ Photo successfully added to the schedule")
    except Exception:
        await message.answer("❌ Error")

    await state.finish()


async def send_calendar_minute_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer("❌ Error\n"
                               "Send a number between 0-59 and no extra characters", reply_markup=cancel_button())

    await state.update_data(msg=msg.message_id)


def register_edit_time(dp: Dispatcher):
    dp.register_message_handler(edit_time, commands=["edit_time"], is_admin=True)
    dp.register_message_handler(get_photo_id, regexp=re.compile(r'^\d+$'), state=AdminEditTime.Id)
    dp.register_message_handler(get_photo_id_validation, state=AdminEditTime.Id)
    dp.register_callback_query_handler(send_calendar, calendar_callback.filter(), state=AdminEditTime.Choose_Calendar)

    dp.register_message_handler(send_calendar_text, state=AdminEditTime.Choose_Calendar,
                                content_types=types.ContentType.ANY)

    dp.register_message_handler(send_calendar_hour, HourFilter(),
                                state=AdminEditTime.Choose_Hour)
    dp.register_message_handler(send_calendar_hour_validation, state=AdminEditTime.Choose_Hour,
                                content_types=types.ContentType.ANY)

    dp.register_message_handler(send_calendar_minute, MinuteFilter(),
                                state=AdminEditTime.Choose_Minute)
    dp.register_message_handler(send_calendar_minute_validation, state=AdminEditTime.Choose_Minute,
                                content_types=types.ContentType.ANY)
