"""Машина состояний"""
from aiogram.dispatcher.filters.state import StatesGroup, State


class GroupStatesInterview(StatesGroup):
    """Машина состояний для работы опросника"""
    name = State()
    business = State()
    stream = State()
    state_of_business = State()
    fire_state = State()
    request = State()
    contact = State()