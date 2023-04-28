from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import logging
from parser import KinoPoisk

from aiohttp import ClientSession

bot = Bot(token='5866193187:AAFSQSyX9RmG2YmkwnMuCVfQmUlMlO2oSh4')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
kinopoisk_fetcher = KinoPoisk()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Здарова!\nЯ CinemaBot и я умею находить '
                         'информацию про твой фильм или сериал и кидать ссылки\n '
                         'напиши любое название и посмотрим там что есть в инете')
# print('start()')

# executor.start_polling(dp)

@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    await message.answer("Пришли пожалуйста название фильма, который ты хочешь найти)")

# print(helper())


@dp.message_handler()
async def search(message: types.Message):
    async with ClientSession() as session:
        imdb = await kinopoisk_fetcher.fetch(session, message.text)
        caption = '{}\nКинопоиск:{}\nСсылка на просмотр: {}'.format(imdb['name'], imdb['rating_kp'], imdb['link_to_watch'])
        media = types.MediaGroup()
        media.attach_photo(imdb['poster'], caption)
        await message.answer_media_group(media)


        # return caption
# print(search())
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
