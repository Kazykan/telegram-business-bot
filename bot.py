"""Бот опросник для бизнес канала"""

import logging
import re


from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,\
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext


from config import TELEGRAM_TOKEN
from sheet import add_to_google_excel
from stategroup import GroupStatesInterview



bot = Bot(token=TELEGRAM_TOKEN)  # Объект бота
dp = Dispatcher(bot,
                storage=MemoryStorage())  # Диспетчер для бота
logging.basicConfig(level=logging.INFO)  # Вкл логирование, чтобы не пропустить важные сообщения


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Запуск начайльной кнопки"""
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать!',
                           reply_markup=get_start_ikb())


def get_start_ikb() -> InlineKeyboardMarkup:
    """Кнопки первые: Записаться, ученику, учителю"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Далее', callback_data='reservation')],
    ], reply_markup=ReplyKeyboardRemove())
    return ikb


def get_answer_y_n_ikb() -> InlineKeyboardButton:
    """Кнопки Да Нет"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Да', callback_data='Yes')],
        [InlineKeyboardButton('Нет', callback_data='No')],
    ], row_width=2)
    return ikb


def get_answer_fire_ikb() -> InlineKeyboardButton:
    """Кнопки Пожар, и не пожар"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Пожар, горит и надо срочно тушить.', callback_data='Fire')],
        [InlineKeyboardButton('Не горит, я пришел послушать', callback_data='okay')],
    ], row_width=2)
    return ikb


def get_answer_busines_question_ikb() -> InlineKeyboardButton:
    """Кнопки разбор пожара"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Хочу получить рекомендации по бизнесу лично', callback_data='personal_meeting')],
        [InlineKeyboardButton('Хочу разобрать на ближайшем стриме', callback_data='stream_repear')],
        [InlineKeyboardButton('Думаю справиться сам', callback_data='myself')],
    ], row_width=2)
    return ikb


def get_answer_account_ikb() -> InlineKeyboardButton:
    """Кнопки разбор пожара"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [KeyboardButton('@rozetked', url='https://t.me/rozetked')],
    ], row_width=2)
    return ikb


@dp.callback_query_handler(text='reservation')
async def cb_add_classtime(callback: types.CallbackQuery) -> None:
    """Начало опроса"""
    await callback.message.delete()
    await callback.message.answer(f'Представьтесь, как ваше Имя\n')
    await GroupStatesInterview.name.set()


@dp.message_handler(state=GroupStatesInterview.name)
async def handle_group_name(message: types.Message, state: FSMContext) -> None:
    """Опрос записываем имя в машину состояния, и продолжаем опрос"""
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply('Напишите, какой у вас бизнес, на чем зарабатываете?')
    await GroupStatesInterview.next()

@dp.message_handler(state=GroupStatesInterview.business)
async def handle_group_business(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['business'] = message.text
    await message.reply('Хотите разобрать ваш бизнес на стриме?',
    reply_markup=get_answer_y_n_ikb())
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='Yes', state=GroupStatesInterview.stream)
async def handle_group_stream(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['stream'] = 'Yes'
    await message.message.delete()
    await message.message.answer('Какая у вас сейчас ситуация в бизнесе?',
    reply_markup=get_answer_fire_ikb())
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='No', state=GroupStatesInterview.stream)
async def handle_group_stream(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['stream'] = 'No'
    await message.message.delete()
    await message.message.answer('Какая у вас сейчас ситуация в бизнесе?',
    reply_markup=get_answer_fire_ikb())
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='Fire', state=GroupStatesInterview.state_of_business)
async def handle_group_state_of_business(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['state_of_business'] = 'Fire'
    await message.message.delete()
    await message.message.answer('Какая у вас сейчас ситуация в бизнесе?',
    reply_markup=get_answer_busines_question_ikb())
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='okay', state=GroupStatesInterview.state_of_business)
async def handle_group_state_of_business(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['state_of_business'] = 'okay'
    await message.message.delete()
    await message.message.answer('Поделитесь вашим телефоном, чтобы не пропустить важные новости')
    await GroupStatesInterview.last()


@dp.callback_query_handler(text='personal_meeting', state=GroupStatesInterview.fire_state)
async def handle_group_fire_state_personal(message: types.Message, state: FSMContext) -> None:
    """Отработка кнопки персональная встреча"""
    async with state.proxy() as data:
        data['fire_state'] = 'Личная встреча'
    await message.message.delete()
    await message.message.answer('Какой у вас запрос?')
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='stream_repear', state=GroupStatesInterview.fire_state)
async def handle_group_fire_state_personal(message: types.Message, state: FSMContext) -> None:
    """Отработка кнопки разобрать на стриме"""
    async with state.proxy() as data:
        data['fire_state'] = 'Разобрать на стриме'
    await message.message.delete()
    await message.message.answer('Какой у вас запрос?')
    await GroupStatesInterview.next()


@dp.callback_query_handler(text='myself', state=GroupStatesInterview.fire_state)
async def handle_group_fire_state_personal(message: types.Message, state: FSMContext) -> None:
    """Отработка кнопки Думаю справиться сам"""
    async with state.proxy() as data:
        data['fire_state'] = 'Думаю справиться сам'
    await message.message.delete()
    await message.message.answer('Поделитесь вашим телефоном, чтобы не пропустить важные новости')
    await GroupStatesInterview.last()


@dp.message_handler(state=GroupStatesInterview.request)
async def handle_group_business(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['request'] = message.text
    await message.reply('Напишите ваш телефон, мы согласуем удобное время и день для консультации')
    await GroupStatesInterview.next()


@dp.message_handler(state=GroupStatesInterview.contact)
async def handle_group_contact(message: types.Message, state: FSMContext) -> None:
    """Добавляем новую группу - 3 пункт"""
    async with state.proxy() as data:
        data['contact'] = message.text
        data['contact_id'] = message.from_user.id
        data['contact_name'] = message.from_user.first_name
        data['contact_lastname'] = message.from_user.last_name
        data['contact_nickname'] = f'@{message.from_user.username}'
    await message.reply('Перейти в канал бизнес-аналитики',
    reply_markup=get_answer_account_ikb())
    add_to_google_excel(data=data)
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)