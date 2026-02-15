import asyncio
import os
import pyodbc
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# ================== НАСТРОЙКИ ==================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.accdb")

TOKEN = "8425896258:AAEU2b8_fMdyfkLMzTZlWopSBEA30LS1RzM"   # <-- просто вставь сюда токен

# ================== БД ==================

def get_connection():
    return pyodbc.connect(
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        rf'DBQ={DB_PATH};'
    )


def fetch_data(query, params):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        conn.close()
        return result

    except Exception as e:
        print("Ошибка БД:", e)
        return []

# ================== ЗАПРОСЫ ==================



def get_user_by_code(code):
    query = """
        SELECT t1.*, t2.[Дата_Візиту]
        FROM Table1 AS t1
        LEFT JOIN Table2 AS t2
            ON t1.[Код] = t2.[ID_Клієнта]
        WHERE t1.[Код]=?
    """
    return fetch_data(query, (code,))


def get_user_by_phone(phone):
    query = """
        SELECT t1.*, t2.[Дата_Візиту]
        FROM Table1 AS t1
        LEFT JOIN Table2 AS t2
            ON t1.[Код] = t2.[ID_Клієнта]
        WHERE t1.[Номер]=?
    """
    return fetch_data(query, (phone,))

# ================== ВСПОМОГАТЕЛЬНОЕ ==================

def format_date(date_value):
    if date_value:
        return date_value.strftime("%d.%m.%Y")
    return "не указана"

def format_money(value):
    if not value:
        return "0 грн"

    value = float(value)

    if value.is_integer():
        return f"{int(value)} грн"

    return f"{value:.2f} грн"

def format_client(data):
    return (
       
        f"🔢 Код: {data.get('Код')}\n"
        f"👤 Имя: {data.get('ПІБ_Клієнта')}\n"
        f"📌 Услуга: {data.get('Тип_Послуги')}\n"
        f"🎟 Куплено сеансов: {data.get('Куплено_Сеансів')}\n"
        f"✔️ Использовано сеансов: {data.get('Використано_Сеансів')}\n"
        f"📅 Завершение: {format_date(data.get('Дата_Завершення'))}\n"
        f"💰 Сумма: {format_money(data.get('Сума_курсу'))}\n"
        f"📱 Телефон: {data.get('Номер')}\n"
        f"🗓 Визит: {format_date(data.get('Дата_Візиту'))}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

# ================== БОТ ==================

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Введите код клиента или номер телефона."
    )


@dp.message()
async def check_client(message: types.Message):

    text = message.text.strip()

    # 1️⃣ Сначала ищем по коду
    users = []
    if text.isdigit():
        users = get_user_by_code(int(text))

    # 2️⃣ Если по коду не нашли — ищем по номеру
    if not users:
        users = get_user_by_phone(text)

    if not users:
        await message.answer("❌ Клиент не найден.")
        return

    response = "✅ Найдено:\n\n"

    for user in users:
        response += format_client(user)

    await message.answer(response)


# ================== ЗАПУСК ==================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())