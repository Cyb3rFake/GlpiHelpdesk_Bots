import os
import logging
import mysql.connector
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
import smtplib
from email.mime.text import MIMEText
import datetime
from os import environ
from dotenv import load_dotenv
from time import sleep

import pathlib

from aiogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm

#Inline keyboard
ticketMenu = ikm(row_width=3)
hlp = ikm(row_width=1)

btnHelp = ikb(text = "HELP!", callback_data="help")
btnSendEmailTicket = ikb(text="Отправить e-mail-заявку", callback_data="email_ticket")
btnSendWebTicket = ikb(text="Отправить web-заявку",callback_data="web_ticket")
ticketMenu.add(btnSendEmailTicket).add(btnSendWebTicket)
hlp.add(btnHelp)

#Env parser
load_dotenv()

#logining for mailserver
logging.basicConfig(level=logging.INFO)

#bot
bot = Bot(token = environ['BOT_SENDER_TOKEN'])
dp = Dispatcher(bot)

#env
smtp_server = 'smtp.mail.ru'
smtp_port = 587
smtp_login = environ['EMAIL']
smtp_password = environ['EMAIL_PASSWORD']
sender_email = environ['EMAIL']
receiver_email = environ['EMAIL']
chatid = environ['CHATID']

http_address = environ['HTTP_ADDRESS']
port = environ['HTTP_PORT']


config = {
    'user':environ['DB_USER'],
    'password': environ['DB_USER_PASSWORD'],
    'host': environ['DB_HOST'],
    'database': environ['DB_NAME'],
    'raise_on_warnings': True
}




def find_db_user(username):
    # print('Бот @Intaro_support_bot онлайн!')



    try:
        # Подключение к базе данных
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
    
        
    except mysql.connector.Error as err:
        return f"Ошибка при подключении к базе данных: {err}"

    # Получаем id и username пользователя из таблицы плагина telegrambot 
    query = "SELECT * FROM glpi_plugin_telegrambot_users gptu  WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        db_user_id = result[0]
        db_tgm_username = result[1]
        # print('Поле Telegram_name запись найдена:',result)
        telegram_db_user_id = result
        
        cursor.execute(f"SELECT realname, name FROM glpi_users WHERE id = {db_user_id}")
        real_name,glpi_login=cursor.fetchone()
        print(real_name,glpi_login,sep='\n')
        return True,real_name,glpi_login
    
    else:
        # print('Телеграм аккаунт в базе не найден')
        return False


        # return False


    # Если запись существует возвращаем (True, Реальное имя пользователя, логин пользователя для GLPI)
    # if result:
    #     query = "SELECT realname, name FROM glpi_users gptu  WHERE id = %s"
    #     # cursor.execute(query, (telegram_db_user_id[0],))
    #     cursor.execute(query, (telegram_db_user_id))
    #     result_1 = cursor.fetchall(),
        
    # elif result_1:        
    #     db_user_realname = result_1[0]
    #     db_user_name = result_1[1]

        

    #     cursor.close()
    #     cnx.close()
    #     return True,db_user_realname,db_user_name
    # else:
        
    #     cursor.close()
    #     cnx.close()
    #     return False,0
    

def start_sender_bot():
    # start_time = datetime.datetime.now().strftime('%H:%M:%S')        
    start_time = datetime.datetime.now()  
       

    async def on_startup(message: types.Message):
        # await bot.send_message(chat_id=chatid, text=f'Бот SENDER Онлайн!\nЗапущен : {start_time.strftime("%D в %Hч : %Mм : %Sс")}')
        print(f'\n\n********* STATUS *********')
        print(f'SenderBot_STATUS: UP\nchat_id : {chatid}\nStart time: {start_time.strftime("%D в %Hч : %Mм : %Sс")}')
        print(f'\n\n ********* END *********')


    async def on_shutdown(message: types.Message):
        finish_time = datetime.datetime.now()
        time_delta = finish_time - start_time
        time_format = time_delta.days, time_delta.seconds // 3600, (time_delta.seconds // 60) % 60, time_delta.seconds % 60
        
        year_days_hours_min_sec=f'{time_format[0]} годы\n{time_format[1]} дни\n{time_format[2]} минуты\n{time_format[3]} секунды'

        # await bot.send_message(chat_id=chatid, text=f'Бот SENDER Оффлайн!\nВыключен в: {finish_time.strftime("%D в %Hч : %Mм : %Sс")}\n--=Проработал=--\n{year_days_hours_min_sec}')
        print(f'\n\n********* STATUS *********')
        print(f'SenderBot_STATUS: DOWN\nchat_id: {chatid}\nUpTime: {year_days_hours_min_sec}')
        print(f'\n\n ********* END *********')


    def send_email(subject, message):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_login, smtp_password)
            server.send_message(msg)


    # /start
    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        
        user_data = find_db_user(message.from_user.username)


        if user_data==None or user_data==False:

            # await bot.send_message(message.chat.id,f'Бот работает, chat_id={message.chat.id}')
            await bot.send_message(message.chat.id,f'Приветстую {message.from_user.username} !\nК сожалению у Вас нет доступа к чат-боту поддержки.\nОбратитесь к системным администраторам или воспользуйтесь инструкциями из Меню.')
            
        else:
            db_username = user_data[1]
            await bot.send_message(
                message.from_user.id, 
                text=f'Приветствую, {db_username} !\nЭто бот поддержки.\nОпишите вашу задачу в тексте сообщения и нажмите отправить. Оставьте Ваш контактный нормер или укажите иной способ обратной связи для сотрудника поддержки.\nВы так же можете отправить заявку через электронную почту или личный кабинет, для этого воспользуйтесь кнопкой HELP',reply_markup=hlp)


    #/help
    @dp.callback_query_handler(text='help')
    async def help_btn(message: types.Message):
        await bot.send_message(message.from_user.id, text=f'Выберите способ отправки нажав на нужную кнопку и проследуйте полученной инструкции.',reply_markup=ticketMenu)
       

    # # /list
    # @dp.message_handler(commands=['list'])
    # async def start_command(message: types.Message):
    #     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #     chatid = message.chat.id
    #     await bot.send_message(message.chat.id,f'Бот работает, chat_id={message.chat.id}')
    #     await bot.send_message(chat_id=chatid,
    #             text=f'Доступные комманды :\n\
    #     /start : welcome message\n\
    #     /chatid : получить id чата\n\
    #     /check_access : проверить возможность отправки заявки\n\
    #     /get_manual : инструкция по отправки заявки в поддержку\n\
    #     /send_telegram_ticket : отправить сообщение в поддежку')




    # # check_access
    # @dp.message_handler(commands=['check_access'])
    # async def check_telegram(message: types.Message):
    #     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #     chatid = message.chat.id
    #     if find_db_user(message.from_user.username)[0]==True:
    #         await bot.send_message(chat_id=chatid, text=f'Вам доступны заявки через телеграмм.')
    #     else:
    #         await bot.send_message(chat_id=chatid, text=f'Вам не доступны заявки через телеграмм.\nДля получения доступа отправьте запрос на почту: glpi_support@intaro.email\nили воспользуйтесь формой заявки по адресу: http://192.168.1.2:8002/')



    # # chatid 
    # @dp.message_handler(commands=['chatid'])
    # async def chatid_command(message: types.Message):

    #     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #     chatid = message.chat.id
    #     await bot.send_message(chat_id=chatid,text=f'CHAT ID : {chatid}')

    @dp.callback_query_handler(text="email_ticket")
    async def web_ticket_btn(message: types.Message):
        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную почту, воспользуйтесь любым доступным почтовым клиентом или сервисом. Откройте новое сообщение, кратко(2-3 слова) опишите тему обращения в заголовке(Тема) письма. В теле письма развернуто опишите задачу и Ваши контактные данные.\nОтправьте сообщение на адрес glpi_support@intaro.email')

    @dp.callback_query_handler(text="web_ticket")
    async def email_ticket(message: types.Message):

        img_path = pathlib.Path(__file__).parent.resolve()

        login_img = InputFile(f'{img_path}/img/M_login.jpeg')
        settings_img = InputFile(f'{img_path}/img/M_Settings.jpeg')
        change_pass_img = InputFile(f'{img_path}/img/M_changepass_1.jpeg')
        exit_img = InputFile(f'{img_path}/img/M_exit.jpeg')
        new_ticket_img =InputFile(f'{img_path}/img/M_newticket.jpeg')

        
        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную через личный кабинет,перейдите по адресу http://{http_address}:{port}. \
                               Пройдите авторизацию, если Вы делаете это впервые, Ваш логин будет {find_db_user(message.from_user.username)[2]} пароль будет 1234567890.')
        await bot.send_photo(message.from_user.id, photo=login_img)
        
        await bot.send_message(message.from_user.id,text=f'Нажмите на заначок шестерни в правом верхнем углу и перейдите раздел настроек профиля.')
        await bot.send_photo(message.from_user.id, photo=settings_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Придумайте новый пароль и заполните поля "Пароль", "Подтверждение пароля".\nНажмите кнопку Сохранить в нижней части окна.')
        await bot.send_photo(message.from_user.id, photo=change_pass_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Перезайдите в личный кабинет с новым паролем, нажав на кнопку со стрелкой в верхнем правом углу')
        await bot.send_photo(message.from_user.id, photo=exit_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Заполните поля заголовок и описание, в заявке оставьте ваши контактные данные.\nНажмите кнопку подтвердить.\nВаша заявка отправлена в поддержку.\nОжидайте обратной связи.')
        await bot.send_photo(message.from_user.id, photo=new_ticket_img)



    @dp.message_handler(commands=['web_instructions'])
    async def email_ticket(message: types.Message):
        img_path = pathlib.Path(__file__).parent.resolve()

        login_img = InputFile(f'{img_path}/img/M_login.jpeg')
        settings_img = InputFile(f'{img_path}/img/M_Settings.jpeg')
        change_pass_img = InputFile(f'{img_path}/img/M_changepass_1.jpeg')
        exit_img = InputFile(f'{img_path}/img/M_exit.jpeg')
        new_ticket_img =InputFile(f'{img_path}/img/M_newticket.jpeg')
        get_login_img = InputFile(f'{img_path}/img/M_get_login.jpeg')


        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную через личный кабинет,перейдите по адресу http://{http_address}:{port}. \
                               Пройдите авторизацию, если Вы делаете это впервые, Вашим логином будет id вашего профиля в личном кабинете https://intaro.bitrix24.ru/. Получить его можно перейдя в настройки профиля и скопировать число в конце адресной строки браузера между двумя слешами, пароль будет 1234567890. После авторизации обязательно измените пароль!')
        
        await bot.send_photo(message.from_user.id, photo=get_login_img)
        sleep(4)
        await bot.send_message(message.from_user.id,text=f'Авторизуйтесь в личном кабинете.\nЛогин:номер профиля bitrix24\nПароль:1234567890\nОБЯЗАТЕЛЬНО ИЗМЕНИТЕ ПАРОЛЬ В ЛК')
        await bot.send_photo(message.from_user.id, photo=login_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Нажмите на заначок шестерни в правом верхнем углу и перейдите раздел настроек профиля.')
        await bot.send_photo(message.from_user.id, photo=settings_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Придумайте новый пароль и заполните поля "Пароль", "Подтверждение пароля".\nНажмите кнопку Сохранить в нижней части окна.')
        await bot.send_photo(message.from_user.id, photo=change_pass_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Перезайдите в личный кабинет с новым паролем, нажав на кнопку со стрелкой в верхнем правом углу')
        await bot.send_photo(message.from_user.id, photo=exit_img)
        sleep(3)
        await bot.send_message(message.from_user.id,text=f'Заполните поля заголовок и описание, в заявке оставьте ваши контактные данные.\nНажмите кнопку подтвердить.\nВаша заявка отправлена в поддержку.\nОжидайте обратной связи.')
        await bot.send_photo(message.from_user.id, photo=new_ticket_img)



    @dp.message_handler(commands=['email_instructions'])
    async def web_ticket_btn(message: types.Message):
        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную почту, воспользуйтесь любым доступным почтовым клиентом или сервисом. Откройте новое сообщение, кратко(2-3 слова) опишите тему обращения в заголовке(Тема) письма. В теле письма развернуто опишите задачу и Ваши контактные данные.\nОтправьте сообщение на адрес glpi_support@intaro.email')



    #mesasges to support
    @dp.message_handler()
    async def handle_message(message: types.Message):
        username = message.from_user.username
        db_chk = find_db_user(username)
        if db_chk==False or db_chk==None:
            await message.reply(f'У Вас нет доступа к отправке заявок через телегерам бота.\nДля отправки заявки в поддержку, воспользуйтесь веб-интерфейсом: http://{http_address}:{port}/\nили отправьте заявку на почту: glpi_support@intaro.email')
        else:

            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            subject = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name

            if last_name!=None:
                send_email(f'Задача от пользователя {first_name, last_name, subject} в {date}', message.text)
            else:
                send_email(f'Задача от пользователя {first_name, subject} в {date}', message.text)
            await message.reply(f'Заявка успешно отправлена в поддержку.🫡')

    executor.start_polling(dp, skip_updates=True)
    # executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
    # executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    






start_sender_bot()
# find_db_user('Cyb3rfake')
# print(find_db_user('jopa'))

# print(print(os.path.abspath(os.getcwd())))
# print(print(os.path.abspath(__file__)))