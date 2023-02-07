from aiogram import Bot, Dispatcher, executor, types
from aiogram.types  import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tokens import TG_TOKEN, GROUP, WELCOME_MSG
from vk_logic import *

storage = MemoryStorage()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
   
btn_open = InlineKeyboardButton('Открыть пост 🗣', callback_data='open')
btn_close = InlineKeyboardButton('Закрыть пост 🤐', callback_data='close')
btn_del = InlineKeyboardButton('Удалить коммент 👮‍♂️', callback_data='delete')
btn_res =  InlineKeyboardButton('Вернуть коммент 🤕', callback_data='restore')
btn_res_post = InlineKeyboardButton ('Вернуть удаленный пост 😰',callback_data= 'restore_post')
btn_ban = InlineKeyboardButton('В бан!⛔️', callback_data='ban')
btn_unban = InlineKeyboardButton('Разбан 🔑', callback_data='unban')
btn_reboot = InlineKeyboardButton('Отправить другую ссылку 🔄\nзавершить работу', callback_data='reboot')

MENU = InlineKeyboardMarkup().row(btn_open, 
btn_close).row(btn_del, 
btn_res).row(btn_res_post).row(btn_ban,
btn_unban).row(btn_reboot)

'''Authorization func. Checking if user is a member of group'''
def user_check(chat_member):
    if chat_member['status'] != 'left' and chat_member['status'] != 'kicked': 
        return True
    else:
        return False

'''FSM class for storing user's link'''
class MessageData(StatesGroup):
    link = State()
    fin = State()

'''/start command handler'''
@dp.message_handler(commands=['start'])
async def welcome_msg(message: types.Message):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        await bot.send_message(message.from_user.id, text= WELCOME_MSG)
        await MessageData.link.set()
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

'''Handler to avoid wrong message'''
@dp.message_handler(lambda message: not message.text.startswith('http'),state= MessageData.link)
async def process_link_invalid(message: types.Message):
    return await message.reply('Принимаю только ссылку!')

'''Link's handler'''
@dp.message_handler(Text(startswith='http'), state = MessageData.link)
async def input_link(message: types.Message, state = FSMContext):
    if user_check(await bot.get_chat_member(chat_id=GROUP,user_id=message.from_user.id)):
        async with state.proxy() as data:
            data['link'] = message.text
        await message.answer(text= 'Что сделать? 🤖', reply_markup=MENU)
        await MessageData.next()
    else:
        await bot.send_message(message.from_user.id,text= 'У вас нет доступа!')

'''Handler for the inline buttons'''
@dp.callback_query_handler(text=['open','close', 'delete', 'restore','restore_post',
'ban','unban','reboot'], state = MessageData.fin)
async def process_callback(call: types.CallbackQuery, state = FSMContext ): 
    if call.data == 'open':
        data = await state.get_data() 
        if vk_open(link_transform(data['link'])):
            await call.message.answer(text='Пост открыт ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'close':
        data = await state.get_data() 
        if vk_close(link_transform(data['link'])):
            await call.message.answer(text='Пост закрыт ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'delete':
        data = await state.get_data()
        if vk_delete(link_transform(data['link'])):
            await call.message.answer(text='Комментарий удален ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'restore':
        data = await state.get_data()
        if vk_restore(link_transform(data['link'])):
            await call.message.answer(text='Комментарий восстановлен ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'restore_post':
        data = await state.get_data()
        if vk_restore_post(link_transform(data['link'])):
            await call.message.answer('Пост восстановлен ✅')
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'ban':
        data = await state.get_data()
        if vk_ban(get_comment(link_transform(data['link']))):
            await call.message.answer('Забанен! ✅')
            await MessageData.fin.set()
        elif vk_ban(screen_name_to_id(data['link'])):
            await call.message.answer('Забанен! ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'unban':
        data = await state.get_data()
        if vk_unban(screen_name_to_id(data['link'])):
            await call.message.answer('Разбанен! ✅')
            await MessageData.fin.set()
        else:
            await call.message.answer(text='Что-то пошло не так!\nЧтобы продолжить нажмите /start')
    if call.data == 'reboot':
        await state.finish()
        await call.message.answer(text='Нажмите /start')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)