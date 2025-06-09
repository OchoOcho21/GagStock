import aiohttp
import asyncio
from db import get_all_chat_ids
from telegram import Bot
from datetime import datetime, timedelta
import traceback

PH_OFFSET = timedelta(hours=8)
ADMIN_ID = 7215748787
last_key = ""

def get_ph_time():
    return datetime.utcnow() + PH_OFFSET

def get_next_reset(minutes_interval):
    now = get_ph_time()
    seconds_since = (now.minute * 60 + now.second) % (minutes_interval * 60)
    return (minutes_interval * 60) - seconds_since

def get_next_hour_reset():
    now = get_ph_time()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return (next_hour - now).seconds

def get_next_7hour_reset():
    now = get_ph_time()
    total_hours = now.hour + now.minute / 60 + now.second / 3600
    next_7h = int((total_hours // 7 + 1) * 7)
    next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=next_7h)
    return (next_reset - now).seconds

def format_time(ts):
    return datetime.fromtimestamp(ts / 1000).strftime('%a %I:%M:%S %p')

async def get_data():
    async with aiohttp.ClientSession() as session:
        gear = await session.get("https://growagardenstock.com/api/stock?type=gear-seeds")
        egg = await session.get("https://growagardenstock.com/api/stock?type=egg")
        weather = await session.get("https://growagardenstock.com/api/stock/weather")
        honey = await session.get("https://growagardenstock.com/api/special-stock?type=honey")
        blood = await session.get("https://growagardenstock.com/api/special-stock?type=blood-twilight")
        cosmetics = await session.get("https://growagardenstock.com/api/special-stock?type=cosmetics")
        night = await session.get("https://kenlie.top/api/gag/stocks/")
        return (
            await gear.json(), await egg.json(), await weather.json(),
            await honey.json(), await blood.json(), await cosmetics.json(), await night.json()
        )

async def check_updates(bot: Bot):
    global last_key
    try:
        gear, egg, weather, honey, blood, cosmetics, night = await get_data()
        now = datetime.now().timestamp() * 1000

        combined = str(gear) + str(egg) + str(weather.get("updatedAt")) + str(honey.get("updatedAt")) + str(blood) + str(cosmetics) + str(night)
        if combined == last_key:
            return
        last_key = combined

        gear_reset = get_next_reset(5)
        egg_reset = get_next_reset(30)
        honey_reset = get_next_hour_reset()
        cosmetics_reset = get_next_7hour_reset()

        stock_message = (
            f"🌾 𝗚𝗿𝗼𝘄 𝗔 𝗚𝗮𝗿𝗱𝗲𝗻 — 𝗦𝘁𝗼𝗰𝗸 𝗨𝗽𝗱𝗮𝘁𝗲\n\n"
            f"🛠️ 𝗚𝗲𝗮𝗿:\n{chr(10).join(gear['gear']) if gear['gear'] else 'No gear stocks yet.'}\n\n"
            f"🌱 𝗦𝗲𝗲𝗱𝘀:\n{chr(10).join(gear['seeds']) if gear['seeds'] else 'No seed stocks yet.'}\n\n"
            f"🥚 𝗘𝗴𝗴𝘀:\n{chr(10).join(egg['egg']) if egg['egg'] else 'No egg stocks yet.'}\n\n"
            f"🩸 𝗕𝗹𝗼𝗼𝗱:\n{chr(10).join(blood.get('blood', [])) if blood.get('blood') else 'No blood stocks yet.'}\n\n"
            f"🌘 𝗧𝘄𝗶𝗹𝗶𝗴𝗵𝘁:\n{chr(10).join(blood.get('twilight', [])) if blood.get('twilight') else 'No twilight stocks yet.'}\n\n"
            f"🧴 𝗖𝗼𝘀𝗺𝗲𝘁𝗶𝗰𝘀:\n{chr(10).join(cosmetics.get('cosmetics', [])) if cosmetics.get('cosmetics') else 'No cosmetic stocks yet.'}\n\n"
            f"Made by: @OchoOcho21"
        )

        weather_message = (
            f"🌤️ 𝗪𝗲𝗮𝘁𝗵𝗲𝗿 𝗨𝗽𝗱𝗮𝘁𝗲\n\n"
            f"{weather.get('icon', '🌦️')} {weather.get('currentWeather', 'Unknown')}\n\n"
            f"📖 {weather.get('description', '')}\n💬 {weather.get('visualCue', '')}\n\n"
            f"🪴 𝗕𝗼𝗻𝘂𝘀: {weather.get('cropBonuses', 'N/A')}\n\n"
            f"Made by: @OchoOcho21"
        )

        reset_message = (
            f"🔁 𝗥𝗲𝘀𝗲𝘁 𝗧𝗶𝗺𝗲𝘀\n\n"
            f"🛠️ 𝗚𝗲𝗮𝗿 / 🌱 𝗦𝗲𝗲𝗱: ⏳ In {gear_reset // 60}m {gear_reset % 60}s\n"
            f"🥚 𝗘𝗴𝗴𝘀: ⏳ In {egg_reset // 60}m {egg_reset % 60}s\n"
            f"🍯 𝗛𝗼𝗻𝗲𝘆: ⏳ In {honey_reset // 60}m {honey_reset % 60}s\n"
            f"🧴 𝗖𝗼𝘀𝗺𝗲𝘁𝗶𝗰𝘀: ⏳ In {cosmetics_reset // 3600}h {(cosmetics_reset % 3600) // 60}m\n\n"
            f"Made by: @OchoOcho21"
        )

        honey_text = "\n".join([f"🍯 {item}" for item in honey.get("honey", [])]) if honey.get("honey") else "No honey stock available."
        honey_message = f"📦 𝗛𝗼𝗻𝗲𝘆 𝗦𝘁𝗼𝗰𝗸\n\n{honey_text}\n\nMade by: @OchoOcho21"

        night_items = night.get("nightStock", [])
        night_text = "\n".join([f"🌌 {item['name']} (x{item['value']})" for item in night_items]) if night_items else "No night stock available."

        easter_items = night.get("easterStock", [])
        easter_text = "\n".join([f"🐣 {item['name']} (x{item['value']})" for item in easter_items]) if easter_items else "No easter stock available."

        special_message = (
            f"🌙 𝗡𝗶𝗴𝗵𝘁 𝗦𝘁𝗼𝗰𝗸\n\n{night_text}\n\n"
            f"🐣 𝗘𝗮𝘀𝘁𝗲𝗿 𝗦𝘁𝗼𝗰𝗸\n\n{easter_text}\n\n"
            f"Made by: @OchoOcho21"
        )

        for chat_id in get_all_chat_ids():
            await bot.send_message(chat_id=chat_id, text=stock_message)
            await bot.send_message(chat_id=chat_id, text=weather_message)
            await bot.send_message(chat_id=chat_id, text=reset_message)
            await bot.send_message(chat_id=chat_id, text=honey_message)
            await bot.send_message(chat_id=chat_id, text=special_message)

    except Exception as e:
        err_msg = f"❌ GAGSTOCK ERROR:\n\n{e}\n\nTraceback:\n{traceback.format_exc()}"
        print(err_msg)
        await bot.send_message(chat_id=ADMIN_ID, text=err_msg[:4096])

async def start_announcer(bot):
    while True:
        await check_updates(bot)
        await asyncio.sleep(30)
