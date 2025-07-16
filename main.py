print('Start')

import os
import telebot
from pytubefix import YouTube
from pytubefix.cli import on_progress
import logging

logging.basicConfig(filename='/home/curiosity/.telebot.log', level=logging.INFO)

TGBOT_TOKEN = os.environ.get('TGBOT_TOKEN')
TGBOT_USER_IDS = os.environ.get('TGBOT_USER_IDS').split(', ')
allowed_user_ids= [int(id) for id in TGBOT_USER_IDS if id]

bot = telebot.TeleBot(TGBOT_TOKEN)

def authorize(func):
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id not in allowed_user_ids:
            bot.reply_to(message, "This is a private bot. You are not authorized to use this bot.")
        else:
            return func(message, *args, **kwargs)
    return wrapper

@bot.message_handler()
@authorize
def save_from(message):
    url = message.text
    chat_id = message.chat.id
    
    # Скачиваем видео
    file_path, error = download_youtube_video(url)
    
    if error:
        bot.reply_to(message, error)
        return
    
    # Отправляем видео в Telegram
    try:
        with open(file_path, 'rb') as video:
            bot.send_video(chat_id, video)
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отправке видео: {e}")
    finally:
        # Удаляем файл после отправки (опционально)
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

def download_youtube_video(url):
    try:       
        yt = YouTube(url, on_progress_callback=on_progress)
        print(yt.title)

        ys = yt.streams.get_highest_resolution()
        file_path = ys.download()
        return file_path, None
    except Exception as e:
        return None, f"Произошла ошибка: {e}"

if __name__ == '__main__':
    try:
        logging.info("Запуск бота...")
        bot.polling()
    except (KeyboardInterrupt, SystemExit):
        pass
