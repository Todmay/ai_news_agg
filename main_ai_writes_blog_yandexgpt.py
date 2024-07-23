from bs4 import BeautifulSoup
import telebot
import random
import requests

from ai_yandexgpt_func import get_gpt_response
#импорт настроек
import settings

news_channel = settings.news_channel  # Замените на имя вашего новостного канала
channels = settings.channels
random.shuffle(channels)

# Инициализация Telegram бота
bot_token = settings.bot_token
bot = telebot.TeleBot(bot_token)


def get_last_post(channel):
    url = f'https://t.me/s/{channel}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = soup.find_all('div', {'class': 'tgme_widget_message_text'})
    if posts:
        return posts[-1].text.strip()
    return None


last_posts = {}
for channel in channels:
    last_posts[channel] = get_last_post(channel)

# Формирование общего текста 
combined_text = "\n\n".join([f"From {channel}:\n{post}" for channel, post in last_posts.items() if post])
prompt = f"ОБЬЕДИНИТЬ ИНФОРМАЦИЮ ИЗ ПОСТОВ И СДЕЛАТЬ ЕДИНУЮ ПУБЛИКАЦИЮ НОВОСТНУЮ С ЗАГОЛОВКАМИ:\n\n{combined_text}"
keywords = " ".join(combined_text.split()[:10]) 
# Получение ответа
news_post = get_gpt_response(prompt)
news_post = f"{news_post}\n * собрано из открытых источников."
# Отправка поста в канал
bot.send_message(chat_id=news_channel, text=news_post)

'''
try:
    # Отправка изображения в новостной канал
    with open('ai-writes-a-blog-lite-lite.png', 'rb') as photo:
        bot.send_photo(news_channel, photo, caption=news_post)
    print("Изображение успешно отправлено в канал")
except Exception as e:
    print(f"Ошибка при отправке изображения в канал: {e}")

'''