import asyncio
from random import randint

import aiogram
import json
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import fitz
from datetime import datetime
import locale

logging.basicConfig(level=logging.INFO)

bot = aiogram.Bot(token="API-KEY")
dp = aiogram.Dispatcher()
dp.bot = bot


def process_data(in_parameter, user_id):
    with open("data.json", "r", encoding="UTF-8") as f:
        data = json.load(f)
    if str(in_parameter) in data:
        with open("user_data.json", "r", encoding="UTF-8") as f:
            user_data = json.load(f)
        user_data[str(user_id)] = {"message": in_parameter}
        with open("user_data.json", "w", encoding="UTF-8") as f:
            json.dump(user_data, f, ensure_ascii=False)
        return True
    else:
        return False


@dp.message(Command("menu"))
async def MenuMenu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="21П-2",
        callback_data="21p2"
    ))
    builder.add(types.InlineKeyboardButton(
        text="21П-1",
        callback_data="21p1"
    ))
    builder.add(types.InlineKeyboardButton(
        text="22ВЕБ-2",
        callback_data="22web2"
    ))
    await message.answer(
        "Нажмите на кнопку, зафиксировать группу за собой",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(aiogram.F.data == "21p2")
async def send_pin_21p2(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    in_parameter = "21П-2"

    if process_data(in_parameter, user_id):
        await callback.message.answer("Текст успешно закреплен за вами.")
    else:
        await callback.message.answer("Введенное вами сообщение не найдено в списке.")


@dp.callback_query(aiogram.F.data == "21p1")
async def send_pin_21p1(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    in_parameter = "21П-1"

    if process_data(in_parameter, user_id):
        await callback.message.answer("Текст успешно закреплен за вами.")
    else:
        await callback.message.answer("Введенное вами сообщение не найдено в списке.")


@dp.callback_query(aiogram.F.data == "22web2")
async def send_pin_21p1(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    in_parameter = "22ВЕБ-2"
    if process_data(in_parameter, user_id):
        await callback.message.answer("Текст успешно закреплен за вами.")
    else:
        await callback.message.answer("Введенное вами сообщение не найдено в списке.")


@dp.message(Command("find"))
async def search(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f"Выполняется поиск...")

    def create_directory(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Директория успешно создана: {directory_path}")
        except FileExistsError:
            print(f"Директория уже существует: {directory_path}")
        except Exception as e:
            print(f"Произошла ошибка при создании директории: {str(e)}")

    def download_file(url, destination):
        response = requests.get(url)
        with open(destination, 'wb') as file:
            file.write(response.content)

    def check_word_in_pdf(url, target_word, exclusion_word):
        try:
            with requests.get(url) as response:
                response.raise_for_status()

                with fitz.open("pdf", response.content) as doc:
                    for page_num in range(doc.page_count):
                        page = doc[page_num]
                        text = page.get_text("text")
                        if target_word in text and exclusion_word not in text:
                            return True

            print(f"Слово '{target_word}' не найдено в PDF: {url}")
            return False

        except requests.RequestException as e:
            print(f"Ошибка при загрузке файла. {str(e)}")
            return False
        except Exception as e:
            print(f"Произошла ошибка при обработке файла: {str(e)}")
            return False

        finally:
            if os.path.exists('pdf'):
                os.remove('pdf')

    async def save_links(download_directory, user_id, result):
        with open("user_data.json", "r", encoding='utf-8') as f:
            user_data = json.load(f)
        for link in links:
            try:
                temp = check_word_in_pdf(link,
                                         target_word=user_data.get(str(user_id), {"none"}).get("message", "none"),
                                         exclusion_word="ЛИКВИДАЦИЯ ЗАДОЛЖЕННОСТЕЙ")
                if temp:
                    result = True
                    break
                else:
                    result = False
                    break
            except Exception as e:
                print(e)

        return result

    download_directory = "C:\\Users\\Feel\\Downloads\\web_parser"  # измените на путь, который вам подходит
    create_directory(download_directory)

    url = "https://www.uksivt.ru/zameny"
    destination = os.path.join(download_directory, "downloaded_file.html")

    download_file(url, destination)
    print(f"Файл успешно скачан по пути: {destination}")

    base_url = "https://www.uksivt.ru/"

    locale.setlocale(locale.LC_TIME, 'ru_RU')
    while True:
        today = datetime.today()
        month = today.strftime("%B").lower()  # Получаем текущий месяц
        day = today.strftime("%d")
        result = False
        with open(destination, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            # day = "26"
            day = day.zfill(2)
            links = [urljoin(base_url, a_tag['href']) for a_tag in soup.find_all('a', href=True) if
                     month.lower() in a_tag['href'].lower() and day in a_tag['href'].lower()]
            if not links:
                await asyncio.sleep(5)
                print("sleep")
            else:
                break
    result = await save_links(download_directory, user_id, result)
    if result:
        await message.reply(f"Ваша группа есть в заменах")
    else:
        await message.reply(f"Вашей группы нету в заменах")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
