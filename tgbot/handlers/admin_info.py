import asyncio

import contextlib
import datetime

from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.infrastucture.database.functions.channel_photo import get_all_channel_photo


async def info_schedule(message: Message, scheduler):
    check_job = 0

    for job in scheduler.get_jobs():
        with contextlib.suppress(Exception):
            if job.id != "send_message_to_channel":
                check_job += 1
                time = str(job.next_run_time).split('+')[0]
                await message.answer_photo(job.kwargs['file_id'], caption=f"{job.id} - {time}")
                await asyncio.sleep(0.03)

    if check_job == 0:
        await message.answer("No schedule image")
    else:
        await message.answer("Done")


async def info_time(message: Message, session, scheduler):
    check_job = 0
    photos = await get_all_channel_photo(session)
    check_first_time = False
    time_date = ''

    interval = scheduler.get_job('send_message_to_channel').trigger.interval
    minute = str(interval).split(':')[1]
    time = (scheduler.get_job(
        'send_message_to_channel').next_run_time - datetime.datetime.now(tz=datetime.timezone.utc)) \
           + datetime.datetime.now()
    first_time = datetime.datetime.strptime(str(time).split('.')[0], '%Y-%m-%d %H:%M:%S')

    for photo in photos:
        if check_first_time is False:
            check_job += 1

            await message.answer_photo(photo.file_id, caption=f"{photo.photo_id} - {first_time}")
            time_date = first_time
            check_first_time = True
        else:
            time_date = time_date + datetime.timedelta(minutes=float(minute))
            other_time = str(time_date).split('.')[0]
            await message.answer_photo(photo.file_id, caption=f"{photo.photo_id} - {other_time}")

        await asyncio.sleep(0.03)

    if check_job == 0:
        await message.answer("No schedule image")
    else:
        await message.answer("Done")


def register_info_time(dp: Dispatcher):
    dp.register_message_handler(info_schedule, commands=["info_schedule"], is_admin=True)
    dp.register_message_handler(info_time, commands=["info_time"], is_admin=True)
