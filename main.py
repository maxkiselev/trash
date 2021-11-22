from config import TG_TOKEN
from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import inline
import logging
import work_db

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        await message.answer('Привет новый пользователь')


@dp.message_handler(commands='list')
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        await message.answer('Выберите действие', reply_markup=inline.start_choice)


class FSMAdmin(StatesGroup):
    add_paper = State()
    del_paper = State()


@dp.message_handler(content_types=['text'], state=FSMAdmin.add_paper)
async def load_add_paper(message: types.Message, state: FSMContext):
    async with state.proxy() as date:
        date['paper'] = '#' + message.text.lower()
        date['user_id'] = message.from_user.id
        chek_paper = work_db.chek_paper_in_db(date['user_id'], date['paper'])
        if len(chek_paper) == 0:
            work_db.add_paper_in_db(date['user_id'], date['paper'])
            await message.answer(f"Добавлен тикер {date['paper']}")
        else:
            await message.answer(f"Тикер {date['paper']} уже добавлен в избранное")
    await message.answer('Действие:', reply_markup=inline.start_choice)
    await state.finish()


@dp.message_handler(content_types=['text'], state=FSMAdmin.del_paper)
async def load_del_paper(message: types.Message, state: FSMContext):
    async with state.proxy() as date:
        date['paper'] = '#' + message.text.lower()
        date['user_id'] = message.from_user.id
        chek_p = work_db.chek_paper_in_db(date['user_id'], date['paper'])
        if len(chek_p) != 0:
            work_db.del_paper_in_db(date['user_id'], date['paper'])
            await message.answer(f"Удален тикер {date['paper']}")
        else:
            await message.answer(f"Тикер {date['paper']} не найден в избранном")
    await message.answer('Действие:', reply_markup=inline.start_choice)
    await state.finish()


@dp.callback_query_handler(text=['add_paper', 'del_paper'])
async def ask_paper(call: types.CallbackQuery):
    if call.data == 'add_paper':
        await FSMAdmin.add_paper.set()
    elif call.data == 'del_paper':
        await FSMAdmin.del_paper.set()
    await bot.send_message(chat_id=call.from_user.id, text="Укажите тикер")


@dp.callback_query_handler(text='my_list')
async def get_my_list(call: types.CallbackQuery):
    my_list = work_db.get_my_list(call.from_user.id)
    prt_message = 'В избранном находятся следующие тикеры: \n'
    for i in my_list:
        prt_message = prt_message + f'{i[0].strip()}\n'
    await bot.send_message(chat_id=call.from_user.id, text=prt_message)


@dp.callback_query_handler(text='cancel')
async def cancel_work(call: types.CallbackQuery):
    await call.answer('Вы отменили операцию')
    await call.message.edit_reply_markup()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
