import logging
import yaml
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
import aiohttp
import uuid

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

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            url + "/files/ask_upload",
            json={"size": os.path.getsize(path)},
            headers=headers,
        )

        if resp.status != 200:
            return resp

        upload_url = (await resp.json())["url"]

        async with aiohttp.ClientSession(headers=headers) as session:
            with open(path, "rb") as file:
                form_data = aiohttp.FormData()
                form_data.add_field("file", file, filename=os.path.basename(path))
                resp = await session.put(upload_url, data=form_data)

                return resp

async def ask_download(url, file_id, token, path=None):
    headers = {
        "Authorization": "OAuth " + token
    }

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            url + "/files/ask_download",
            json={"file_id": file_id},
            headers=headers,
        )

        if resp.status != 200:
            print(f"[{resp.status}] Something went wrong:", (await resp.json())["message"])
            return resp, None

        print("Downloading the file...")
        download_url = (await resp.json())["url"]
        
        resp = await session.get(
            download_url,
            headers=headers,
        )

        if resp.status != 200:
            print(f"[{resp.status}] Something went wrong:", (await resp.json())["message"])
            return resp, None

        full_path = path
        disp = resp.headers.get("Content-Disposition", "")
        if "filename=" in disp:
            path = disp.split("filename=")[-1].strip('"')
        else:
            path = str(uuid.uuid4()) + '.bin'
        full_path = os.path.join(full_path, path)

        with open(full_path, "wb") as f:
            while chunk := await resp.content.read(16 * 1024):
                f.write(chunk)
        return resp, full_path



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
    json = await resp.json()

    if resp.status != 200:
        await message.reply(f'[{resp.status}] Something went wrong: {json["message"]}')
    else:
        await message.reply(f"Success! File ID: {json['file_id']}")

@dp.message_handler(commands=['download'])
async def handle_download(message: types.Message):
    file_id = message.text.split(' ')[-1]
    print(file_id)
    url = os.getenv("BOT_REQUEST_URL")
    url = url.removesuffix('/')
    resp, path = await ask_download(url, file_id, os.getenv("USER_TOKEN"), os.getenv("BOT_FILES_PATH"))
    print("Finished! Result path:", path)
    if resp.status != 200:
        await message.reply("Something went wrong")
    else:
        with open(path, "rb") as file:
            await message.reply_document(document=file, caption="Requested file")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)