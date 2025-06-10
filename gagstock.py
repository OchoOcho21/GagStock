import aiohttp
import asyncio
from db import get_all_chat_ids, remove_chat_id, load_stock_cache, save_stock_cache
from telegram import Bot
from datetime import datetime, timedelta
import traceback

PH_OFFSET = timedelta(hours=8)
ADMIN_ID = 7215748787

get_ph_time = lambda: datetime.utcnow() + PH_OFFSET
get_next_reset = lambda m: (m * 60) - ((get_ph_time().minute * 60 + get_ph_time().second) % (m * 60))
def get_next_hour_reset(): return (get_ph_time().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1) - get_ph_time()).seconds
def get_next_7hour_reset():
    now = get_ph_time()
    next_7h = int((now.hour + now.minute / 60 + now.second / 3600) // 7 + 1) * 7
    reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=next_7h)
    return (reset_time - now).seconds

def compare_stock(old: dict, new: dict, category: str) -> str:
    diff_lines = [f"\n\n• {category.capitalize()}:\n"]
    old_items = old or {}
    new_items = new or {}
    all_keys = set(old_items.keys()) | set(new_items.keys())
    for key in sorted(all_keys):
        old_val = old_items.get(key)
        new_val = new_items.get(key)
        if old_val and not new_val:
            diff_lines.append(f"  [❎] {key}: disappeared")
        elif not old_val and new_val:
            diff_lines.append(f"  [✅] {key}: {new_val} appeared")
        elif old_val != new_val:
            diff_lines.append(f"  [♻️] {key}: {old_val} → {new_val}")
    return "\n".join(diff_lines) if len(diff_lines) > 1 else ""

def normalize_stock(data: list) -> dict:
    result = {}
    for item in data:
        if isinstance(item, str):
            result[item.strip()] = 1
        elif isinstance(item, dict):
            result[item["name"]] = item.get("value", 1)
    return result

async def check_updates(bot: Bot):
    try:
        async with aiohttp.ClientSession() as session:
            gear = await session.get("https://growagardenstock.com/api/stock?type=gear-seeds")
            egg = await session.get("https://growagardenstock.com/api/stock?type=egg")
            weather = await session.get("https://growagardenstock.com/api/stock/weather")
            honey = await session.get("https://growagardenstock.com/api/special-stock?type=honey")
            blood = await session.get("https://growagardenstock.com/api/special-stock?type=blood-twilight")
            cosmetics = await session.get("https://growagardenstock.com/api/special-stock?type=cosmetics")
            night = await session.get("https://kenlie.top/api/gag/stocks/")

            gear, egg, weather, honey, blood, cosmetics, night = (
                await gear.json(), await egg.json(), await weather.json(),
                await honey.json(), await blood.json(), await cosmetics.json(), await night.json()
            )

        current = {
            "gear": normalize_stock(gear.get("gear", [])),
            "seeds": normalize_stock(gear.get("seeds", [])),
            "egg": normalize_stock(egg.get("egg", [])),
            "honey": normalize_stock(honey.get("honey", [])),
            "cosmetics": normalize_stock(cosmetics.get("cosmetics", []))
        }

        previous = load_stock_cache()
        diffs = [compare_stock(previous.get(key), current[key], key) for key in current]
        change_message = "\n".join([d for d in diffs if d.strip()])

        if not change_message:
            return

        save_stock_cache(current)

        now = get_ph_time().strftime("%m/%d/%Y, %I:%M:%S %p")
        reset_in = get_next_reset(5)
        full_msg = (
            f"🔔 Stock Changes Detected @ {now}\n\n"
            f"• {reset_in // 60} min's left to get it.\n"
            + change_message + "\n\nMade by: @OchoOcho21"
        )

        for chat_id in get_all_chat_ids():
            try:
                await bot.send_message(chat_id=chat_id, text=full_msg)
            except Exception as e:
                if "Chat not found" in str(e):
                    remove_chat_id(chat_id)
                else:
                    raise

    except Exception as e:
        err_msg = f"❌ GAGSTOCK ERROR:\n\n{e}\n\nTraceback:\n{traceback.format_exc()}"
        print(err_msg)
        await bot.send_message(chat_id=ADMIN_ID, text=err_msg[:4096])

async def start_announcer(bot):
    while True:
        await check_updates(bot)
        await asyncio.sleep(30)
