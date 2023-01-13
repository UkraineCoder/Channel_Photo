from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='❌ Cancel', callback_data="admin_cancel")
        ]
    ])

    return keyboard