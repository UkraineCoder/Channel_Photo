from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from tgbot.infrastucture.database.functions.channel_photo import get_channel_photo, delete_channel_photo
from tgbot.inline.buttons import cancel_button
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import DeleteTime


async def check_all_id(message: Message, all_id):
    if all_id:
        await message.answer(f"Deleted photos with id: {', '.join(all_id)}")
    else:
        await message.answer("No photos with such id")


async def get_photo_id(message: Message, state: FSMContext):
    msg = await message.answer('Enter the ID of the image you want to delete', reply_markup=cancel_button())

    await state.update_data(msg=msg.message_id)

    await DeleteTime.Id.set()


async def delete_time(message: Message, state: FSMContext, session, scheduler):
    await delete_markup(message, state)

    check_separated = message.text.split('\n')
    to_str = ' '.join(check_separated)
    photos = to_str.split(' ')

    for check_int in photos:
        try:
            int(check_int)
        except ValueError:
            msg = await message.answer("Enter only numbers separated by spaces", reply_markup=cancel_button())
            await state.update_data(msg=msg.message_id)
            return

    all_id = []

    for photo in photos:
        photo_check = await get_channel_photo(session, photo_id=int(photo))
        if photo_check:
            await delete_channel_photo(session, photo_id=int(photo))
            all_id.append(photo)

    photos_time = message.text.split(' ')

    for photo in photos_time:
        for job in scheduler.get_jobs():
            if job.id == photo:
                scheduler.remove_job(job.id)
                all_id.append(photo)

    await check_all_id(message, all_id)

    await state.finish()


async def delete_time_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer("Enter only numbers separated by spaces", reply_markup=cancel_button())
    await state.update_data(msg=msg.message_id)


def register_delete_time(dp: Dispatcher):
    dp.register_message_handler(get_photo_id, commands=["delete_time"], is_admin=True)
    dp.register_message_handler(delete_time, regexp=r'\d+', state=DeleteTime.Id)
    dp.register_message_handler(delete_time_validation, state=DeleteTime.Id)