from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminEditTime(StatesGroup):
    Id = State()
    Choose_Calendar = State()
    Choose_Hour = State()
    Choose_Minute = State()


class AdminTotalTime(StatesGroup):
    Time = State()


class AdminDelete(StatesGroup):
    Id = State()


class DeleteTime(StatesGroup):
    Id = State()


class AdminNew(StatesGroup):
    Id = State()
