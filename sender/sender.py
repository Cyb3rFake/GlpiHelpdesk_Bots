import logging
import mysql.connector
from aiogram import Bot, Dispatcher, executor, types
import smtplib
from email.mime.text import MIMEText
import datetime
from os import environ
from dotenv import load_dotenv

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


print('Бот @Intaro_support_bot онлайн!')


def find_db_user(username):
    try:
        # Подключение к базе данных
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
    

        query = "SELECT * FROM glpi_plugin_telegrambot_users gptu  WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        telegram_db_user=result

        # print("Пользователь найден!")
        # print("ID:", result[0])
        # print("USERNAME(TELEGRAM):", result[1])
        # print("ID:", result[0])
        # print("Имя пользователя:", result[1])
        # print("Email:", result[2])

        if result:
            query = "SELECT realname FROM glpi_users gptu  WHERE id = %s"
            cursor.execute(query, (telegram_db_user[0],))
            db_user_realname = cursor.fetchone()
            return True,*db_user_realname
        else:
            return False,0
        
    except mysql.connector.Error as err:
        return None,None,f"Ошибка при подключении к базе данных: {err}"
    


        #     # user_id = result[0]
        #     # user_name = result[0]
        #     return True, result
        #     print("Пользователь найден!")
        #     print("ID:", result[0])
        #     # print("USERNAME(TELEGRAM):", result[1])
        #     # print("ID:", result[0])
        #     # print("Имя пользователя:", result[1])
        #     # print("Email:", result[2])
        # else:
        #     return False, None
        #     print("Пользователь не найден.")

        
        query = "SELECT realname FROM glpi_users gptu  WHERE id = %s"
        cursor.execute(query, (telegram_db_user[0],))
        result = cursor.fetchone()

        # print(*[i for i in result if not any[i==0,i==None,i=='']])
        # print('REALNAME:',result[0])
        # print('LOGIN_NAME:',result[1])
        # print('DATE_CREATION:',result[2])
        # print('CREATED IN:',result[1])


        cursor.close()
        cnx.close()


def start_sender_bot():
    # start_time = datetime.datetime.now().strftime('%H:%M:%S')        
    start_time = datetime.datetime.now()  
        
    async def on_startup(message: types.Message):
        # await bot.send_message(chat_id=chatid, text=f'Бот SENDER Онлайн!\nЗапущен : {start_time.strftime("%D в %Hч : %Mм : %Sс")}')
        print(f'\n\n********* STATUS *********')
        print(f'SenderBot_STATUS: UP\nchat_id : {chatid}\nat: {start_time}\nStart time: {start_time.strftime("%D в %Hч : %Mм : %Sс")}')
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
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        if find_db_user(message.from_user.username)[0] == False:

            # await bot.send_message(message.chat.id,f'Бот работает, chat_id={message.chat.id}')
            await bot.send_message(message.chat.id,f'Приветстую {message.from_user.username} !\nК сожалению у Вас нет доступа к чат-боту поддержки.\nОбратитесь к системным администраторам.')
            
        else:
            db_username = find_db_user(message.from_user.username)[1]
            await bot.send_message(
                message.from_user.id, 
                text=f'Приветствую, {db_username} !\nЭто бот поддержки.\nОпишите важу задачу в тексте сообщения. Оставьте Вашь контактный нормерь или укажите иной способ обратной связи для сотрудника поддержки.\nВы так же можете отправить заявку через электронную почту или приложение этого воспользуйтесь кнопкой HELP',reply_markup=hlp)

    # /help
    @dp.message_handler(commands=['help1'])
    async def start_command(message: types.Message):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        chatid = message.chat.id
        await bot.send_message(message.chat.id,f'Бот работает, chat_id={message.chat.id}')
        await bot.send_message(chat_id=chatid,
                text=f'Доступные комманды :\n\
        /start : welcome message\n\
        /chatid : получить id чата\n\
        /check_access : проверить возможность отправки заявки\n\
        /get_manual : инструкция по отправки заявки в поддержку\n\
        /send_telegram_ticket : отправить сообщение в поддежку')



    #/help
    @dp.callback_query_handler(text='help')
    async def help_btn(message: types.Message):
        await bot.send_message(message.from_user.id, text=f'Выберите способ отправки нажав на нужную кнопку и проследуйте полученной инструкции.',reply_markup=ticketMenu)
       

    # check_access
    @dp.message_handler(commands=['check_access'])
    async def check_telegram(message: types.Message):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        chatid = message.chat.id
        if find_db_user(message.from_user.username)[0]==True:
            await bot.send_message(chat_id=chatid, text=f'Вам доступны заявки через телеграмм.')
        else:
            await bot.send_message(chat_id=chatid, text=f'Вам не доступны заявки через телеграмм.\nДля получения доступа отправьте запрос на почту: glpi_support@intaro.email\nили воспользуйтесь формой заявки по адресу: http://192.168.1.2:8002/')



    # chatid 
    @dp.message_handler(commands=['chatid'])
    async def chatid_command(message: types.Message):

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        chatid = message.chat.id
        await bot.send_message(chat_id=chatid,text=f'CHAT ID : {chatid}')


    @dp.callback_query_handler(text="email_ticket")
    async def web_ticket_btn(message: types.Message):
        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную почту, воспользуйтесь любым доступным почтовым клиентом или сервисом. Откройте новое сообщение, кратко(2-3 слова) опишите тему обращения в заголовке(Тема) письма. В теле письма развернуто опишите задачу и Ваши контактные данные.\nОтправьте сообщение на адрес glpi_support@intaro.email')


    @dp.callback_query_handler(text="web_ticket")
    async def email_ticket(message: types.Message):
        await bot.send_message(message.from_user.id,text=f'Для отправки заявки через электронную через личный кабинет,перейдите по адресу http://{http_address}:{port} . Пройдите авторизацию, перейдитите во вкладку заявки и нажимте на +, заполните поля и нажмите кнопку Добавить в нижней части экрана.')


    #others
    @dp.message_handler()
    async def handle_message(message: types.Message):
        username = message.from_user.username
        if find_db_user(username)[0]==True:
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            subject = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name

            if last_name!=None:
                send_email(f'Задача от пользователя {first_name, last_name, subject} в {date}', message.text)
            else:
                send_email(f'Задача от пользователя {first_name, subject} в {date}', message.text)
            await message.reply(f'Заявка успешно отправлена в поддержку.')
        else:
            await message.reply(f'К сожалению Ваш телеграм аккаунт "{username}" не занесен в базу данных.\nДля отправки заявки в поддержку, воспользуйтесь веб-интерфейсом: http://{http_address}:{http_port}/\nили отправьте заявку на почту: glpi_support@intaro.email')

    # executor.start_polling(dp, skip_updates=True)
    # executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)

    
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    



start_sender_bot()
