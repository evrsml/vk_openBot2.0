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

storage = MemoryStorage()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
   
btn_open = InlineKeyboardButton('Открыть пост', callback_data='open')
btn_close = InlineKeyboardButton('Закрыть пост', callback_data='close')
btn_del = InlineKeyboardButton('Удалить комментарий', callback_data='delete')
btn_res =  InlineKeyboardButton('Восстановить коммент', callback_data='restore')

MENU = InlineKeyboardMarkup().add(btn_open, btn_close, btn_del, btn_res)

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
    #global res_id
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
    return res_id
    
def vk_open(data):
    if vk_api.wall.openComments(owner_id = data[0], post_id = data[1]):
        return True
    else:
        False

def vk_close(data):
    if vk_api.wall.closeComments(owner_id = data[0], post_id = data[1]):
        return True
    else:
        False

class MessageData(StatesGroup):

    link = State()
    fin = State()

@dp.message_handler(commands=['start'])
async def welcome_msg(message: types.Message, state = FSMContext):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        await MessageData.link.set()
        await bot.send_message(message.from_user.id, text='''Бот умеет открывать, закрывать, удалять и восстанавливать комментарии на следующих страницах Вконтакте:\n 
Радий Хабиров\n
Администрация Главы РБ\n
ЦУР Башкортостан\n\nОтправьте ссылку в ответ, чтобы открыть или закрыть пост''')
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

@dp.message_handler(Text(startswith='http'),state=MessageData.link)
async def input_link(message: types.Message, state: FSMContext):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        async with state.proxy() as data:
            data['link'] = message.text
        await MessageData.next()
        await message.answer(text= 'Что сделать?',reply_markup=MENU)
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

@dp.callback_query_handler(text=['open','close', 'delete', 'restore'], state = MessageData.fin)
async def process_callback(call: types.CallbackQuery,state = FSMContext ):
    if call.data == 'open':
        data = await state.get_data() 
        await state.finish()
        if vk_open(link_transform(data['link'])):
            await call.message.answer(text='Пост открыт!')
        else:
            await call.message.answer(text='Что-то пошло не так!')
    if call.data == 'close':
        data = await state.get_data() 
        await state.finish()
        if vk_close(link_transform(data['link'])):
            await call.message.answer(text='Пост закрыт!')
        else:
            await call.message.answer(text='Что-то пошло не так!')
    if call.data == 'delete':
        data = await state.get_data()
        await state.finish()
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)