import vk
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types  import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tokens import VK_TOKEN, TG_TOKEN, GROUP
import logging

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)
   
btn_post = InlineKeyboardButton('Опубликовать', callback_data='post_comment')
btn_del = InlineKeyboardButton('Удалить', callback_data='delete_comment')
btn_like = InlineKeyboardButton('Поставить лайк', callback_data='like')

MENU_ACTION = InlineKeyboardMarkup().add(btn_post)
DEL_COMMENT = InlineKeyboardMarkup().add(btn_del)

logging.basicConfig(level=logging.DEBUG)

vk_api = vk.API(access_token=VK_TOKEN, v= '5.131')

'''функция авторизации. Проверяет состоит ли пользователь в группе'''
def user_check(chat_member):
    print(chat_member['status'])
    if chat_member['status'] != 'left' and chat_member['status'] != 'kicked': 
        return True
    else:
        return False

'''здесь преобразуем ссылку в нужный формат для ВК апи'''
def link_transform(link):
    global res_id
    res_id = ['','',''] 
    pattern_comment = r"_r+\d+|reply=\d+"
    pattern_post = r"-?\d+_\d+"
    res_post = re.findall(pattern_post, link)
    res_comment = re.findall(pattern_comment, link)
    if len(res_comment) == 0:
        result_id = res_post[0].split('_')
        res_id[0] = result_id[0]
        res_id[1] = result_id[1]
    else:
        result_id = res_post[0].split('_')
        if res_comment[0].startswith('_r'):
            result_id_rep = res_comment[0].split('_r')
        else:
            result_id_rep = res_comment[0].split('reply=')
        res_id[0] = result_id[0]
        res_id[1] = result_id[1]
        res_id[2] = result_id_rep[1]
    print(res_id)
    return res_id


@dp.message_handler(commands=['start'])
async def welcome_msg(message: types.Message):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        await bot.send_message(message.from_user.id, text='''Бот умеет открывать, закрывать, удалять и восстанавливать комментарии на следующих страницах Вконтакте:\n 
Радий Хабиров\n
Администрация Главы РБ\n
ЦУР Башкортостан\n\nОтправьте ссылку в ответ, чтобы открыть или закрыть пост''')
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

@dp.message_handler()
async def input_link(message: types.Message):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        link = link_transform(message.text)
        await message.answer(text= 'Что сделать?',reply_markup=MENU)
        return link
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

@dp.callback_query_handler(text=['open_post','close_post'])
async def process_callback(call: types.CallbackQuery):
    if call.data == 'open_post':
        print(res_id)
        api.wall.openComments(owner_id = res_id[0], post_id = res_id[1])
        await call.message.answer(text='Пост Радия Хабирова открыт!')
    if call.data == 'close_post':
        print(res_id)
        api.wall.closeComments(owner_id = res_id[0], post_id = res_id[1])
        await call.message.answer(text='Пост Радия Хабирова закрыт!')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)