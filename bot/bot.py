import logging
import yaml
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
import aiohttp
import uuid
from async_requests.async_requests import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

if not os.path.exists('files'):
    os.makedirs('files')

with open("messages/messages.yml", "r") as file:
    messages = yaml.safe_load(file)

async def on_startup(dp):
    print("bot started")

async def on_shutdown(dp):
    await bot.close()

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer(messages["help"])


async def ask_upload(url, path, token):
    headers = {
        "Authorization": "OAuth " + token
    }

    resp = await async_post(
        url + "/files/ask_upload",
        json={
            "size": os.path.getsize(path),
            "access": "PUBLIC"
        },
        headers=headers
    )

    if resp['status'] != 200:
        return resp

    resp = await async_upload_file_put(resp['json']['url'], path, headers=headers)

    return resp


async def ask_download_link(url, file_id, token):
    headers = {
        "Authorization": "OAuth " + token
    }

    resp = await async_post(
        url + "/files/ask_download",
        json = {"file_id": file_id},
        headers=headers
    )
    return resp


@dp.message_handler(content_types=['document'])
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)

    file_name = file.file_path.split('/')[-1]
    file_path = os.path.join('files', file_name)

    await bot.download_file(file.file_path, file_path)

    url = os.getenv("BOT_REQUEST_URL")
    url = url.removesuffix('/')
    resp = await ask_upload(url, file_path, os.getenv("USER_TOKEN"))

    if resp['status'] != 200:
        await message.reply(f'[{resp["status"]}] Something went wrong: {resp["text"]}')
    else:
        await message.reply(f"Success! Download link: {url + '/files/download/' + resp['json']['file_id']}")

# def make_message(resp):
#     print(resp['result'])
#     ans = ''
#     for item in resp['result']:
#         ans += item['file_id'] + '\n'
#     return ans

# @dp.message_handler(commands=['list'])
# async def handle_list(message: types.Message):
#     headers = {
#         "Authorization": "OAuth " + os.getenv("USER_TOKEN")
#     }
#     url = os.getenv("BOT_REQUEST_URL")
#     url = url.removesuffix('/')
#     resp = await async_get(
#         url + '/files/list',
#         headers=headers
#     )
#     await message.reply(make_message(eval(resp['text'])))


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)