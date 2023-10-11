import telebot
import imaplib
import email
import time
from dotenv import load_dotenv
from os import environ

load_dotenv()

#Параметры подключения к телеграмм боту
bot_token = environ['BOT_NOTIFIER_TOKEN']
bot_chat_id = environ['CHATID']

# Параметры подключения к почтовому серверу
imap_server = environ['MAILSERVER']
username = environ['EMAIL']
password = environ['EMAIL_PASSWORD']
check_timer = int(environ['CHECK_TIMER'])

# Устанавливаем подключение к телеграмм боту
bot = telebot.TeleBot(bot_token)

# Функция для отправки сообщения в телеграмм канал
def send_message(message):
    bot.send_message(bot_chat_id, message)

# Функция для получения последнего письма с почтового ящика
def get_latest_email():
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select('inbox')

    result, data = mail.search(None, 'UNSEEN')
    if result == "OK":
        message_nums = data[0].split()
        if len(message_nums) <= 0:
            return None

    latest_email_id = data[0].split()[-1]
    
    result, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    
    email_message = email.message_from_bytes(raw_email)

    sender = email.utils.parseaddr(email_message['From'])[1]
    
    # Декодирование заголовка
    subject = email_message['Subject']
    decoded_header = email.header.decode_header(subject)
    decoded_string = ""
    for part, encoding in decoded_header:
        if isinstance(part, bytes):
            if encoding:
                decoded_string += part.decode(encoding)
            else:
                decoded_string += part.decode()
        else:
            decoded_string += part
    subject = decoded_string

    # Получаем дату получения письма
    received_time = email_message['Date']

    text = ''
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                text = part.get_payload(decode=True).decode()
                break
    else:
        text = email_message.get_payload(decode=True).decode()
    
    mail.close()
    mail.logout()
    print('\nData received:')
    # print(f'{sender}, {subject}, {received_time}, {text}',sep='\n')
    return sender, subject, received_time, text


def runer():
    # Основной цикл программы
    print('Bot Notifier: Online <3')
    while True:
        get_data = get_latest_email()
        if get_data==None:
            time.sleep(check_timer)
            continue

        sender, subject, received_time, text = get_data
        
        message = f"Отправтель: {subject}\nПолучено в :\n{received_time}\nТекст заявки : \n{text}"
        # message = f"Sender: {sender}\nSubject: {subject}\nReceived at: {received_time}\n\n{text}"
        print(message)
        send_message(message)
        
        time.sleep(check_timer)  # Ожидание в секундах секунды перед получением нового письма

if __name__=='__main__':
    runer()