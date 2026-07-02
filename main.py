import os
import asyncio
import random
import time
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fastapi import FastAPI, Request

load_dotenv()
TOKEN = "8985813448:AAGXur6r5-pPMr9hEqYv4597-C8qd0cozOc"
RENDER_URL = "https://yordamchi-bot-bi29.onrender.com" 
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users_db = {}
group_status = {"mode": "day"}

def get_user_data(user_id, name="Foydalanuvchi"):
    if user_id not in users_db:
        users_db[user_id] = {
            "name": name, "id": user_id,
            "joined": datetime.now().strftime("%d.%m.%Y"),
            "messages": 0, "warns": 0, "role": "Oddiy a'zo",
            "rights": {"is_main": False, "is_admin": False, "is_mod": False, "is_muter": False}
        }
    return users_db[user_id]
async def check_is_admin(message: types.Message, required_right=None):
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True
    u = get_user_data(message.from_user.id)
    if u["rights"]["is_main"] or u["rights"]["is_admin"]:
        return True
    if required_right == "mod" and u["rights"]["is_mod"]:
        return True
    if required_right == "muter" and u["rights"]["is_muter"]:
        return True
    try:
        member = await message.chat.get_member(message.from_user.id)
        if member.status in ["creator", "administrator"]:
            return True
    except:
        pass
    return False

def get_mention(user: types.User):
    return f"[{user.full_name}](tg://user?id={user.id})"

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def global_message_handler(message: types.Message):
    if message.text and message.text.startswith("/"):
        return
    if not message.sender_chat:
        user = get_user_data(message.from_user.id, message.from_user.full_name)
        user["messages"] += 1
    if group_status["mode"] == "night":
        if not await check_is_admin(message):
            try:
                await message.delete()
            except:
                pass
            return
@dp.message(Command("main"))
async def make_main(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return await message.reply("Foydalanuvchi xabariga reply qiling!")
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Eng oliy admin 👑"
    t_user["rights"]["is_main"] = True
    t_user["rights"]["is_admin"] = True
    await message.reply(f"👑 Mondoshim {get_mention(target)} eng oliy admin etib tayinlandi! (Anonimlikdan tashqari to'liq nazorat)", parse_mode="Markdown")

@dp.message(Command("unmain"))
async def remove_main(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Oddiy a'zo"
    t_user["rights"] = {"is_main": False, "is_admin": False, "is_mod": False, "is_muter": False}
    await message.reply(f"❌ {get_mention(target)} barcha bosh adminlik huquqlaridan mahrum qilindi va oddiy a'zoga aylantirildi.", parse_mode="Markdown")

@dp.message(Command("admin"))
async def make_admin(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Guruh Admini 🛠"
    t_user["rights"]["is_admin"] = True
    await message.reply(f"🛠 {get_mention(target)} guruh admini darajasiga ko'tarildi.", parse_mode="Markdown")

@dp.message(Command("unadmin"))
async def remove_admin(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Oddiy a'zo"
    t_user["rights"]["is_admin"] = False
    await message.reply(f"❌ {get_mention(target)}dan adminlik huquqlari qaytarib olindi.", parse_mode="Markdown")

@dp.message(Command("moderator"))
async def make_mod(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Moderator 🛡"
    t_user["rights"]["is_mod"] = True
    await message.reply(f"🛡 {get_mention(target)} guruh moderatori qilib tayinlandi (Xabarlarni o'chirish va cheklash huquqi bilan).", parse_mode="Markdown")

@dp.message(Command("unmoderator"))
async def remove_mod(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Oddiy a'zo"
    t_user["rights"]["is_mod"] = False
    await message.reply(f"❌ Moderatordan barcha huquqlar qaytarib olindi.")

@dp.message(Command("muter"))
async def make_muter(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["role"] = "Muter 🔇"
    t_user["rights"]["is_muter"] = True
    await message.reply(f"🔇 {get_mention(target)}ga faqat boshqa o'yinchilarni mut qilish huquqi berildi.", parse_mode="Markdown")

@dp.message(Command("unmuter"))
async def remove_muter(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["rights"]["is_muter"] = False
    await message.reply(f"❌ Foydalanuvchidan mut qilish huquqi qaytarib olindi.")
@dp.message(Command("mute"))
async def mute_user(message: types.Message, command: CommandObject):
    if not (await check_is_admin(message) or await check_is_admin(message, "mod") or await check_is_admin(message, "muter")):
        return
    if not message.reply_to_message:
        return await message.reply("Foydalanuvchi xabariga reply qiling!")
    args = command.args
    if not args:
        return await message.reply("Vaqt va sababni yozing. Misol: `/mute 10m qoida`")
    parts = args.split(" ", 1)
    time_str = parts[0]
    reason = parts[1] if len(parts) > 1 else "Sabab ko'rsatilmadi"
    unit = time_str[-1]
    try:
        duration = int(time_str[:-1])
    except ValueError:
        return await message.reply("Vaqt formati noto'g'ri. Misol: 10m, 2h, 1d")
    seconds = duration * 60 if unit == 'm' else duration * 3600 if unit == 'h' else duration * 86400 if unit == 'd' else 0
    if seconds == 0: return await message.reply("Noto'g'ri vaqt o'lchovi.")
    until_date = int(time.time() + seconds)
    target = message.reply_to_message.from_user
    try:
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=target.id, permissions=types.ChatPermissions(can_send_messages=False), until_date=until_date)
        await message.reply(f"🔇 {get_mention(target)} {time_str} ga ovozdan mahrum qilindi.\nSabab: {reason}", parse_mode="Markdown")
    except:
        await message.reply("Xatolik: Botda adminlik huquqlari yetarli emas.")

@dp.message(Command("unmute"))
async def unmute_user(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    try:
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=target.id, permissions=types.ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
        await message.reply(f"🔊 {get_mention(target)} blokdan chiqarildi, guruhda gapirishi mumkin.", parse_mode="Markdown")
    except:
        await message.reply("Xatolik yuz berdi.")

@dp.message(Command("warn"))
async def warn_user(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["warns"] += 1
    if t_user["warns"] >= 3:
        t_user["warns"] = 0
        until_date = int(time.time() + 86400)
        try:
            await bot.restrict_chat_member(chat_id=message.chat.id, user_id=target.id, permissions=types.ChatPermissions(can_send_messages=False), until_date=until_date)
            await message.reply(f"⚠️ {get_mention(target)}da ogohlantirishlar soni 3 taga yetdi! Bot uni avtomatik 24 soatga mut qildi.", parse_mode="Markdown")
        except:
            await message.reply(f"⚠️ Ogohlantirish 3 taga yetdi, lekin bot cheklay olmadi.")
    else:
        await message.reply(f"⚠️ {get_mention(target)} ogohlantirish oldi. Jami ogohlantirishlari: {t_user['warns']}/3", parse_mode="Markdown")

@dp.message(Command("unwarn"))
async def unwarn_user(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    t_user = get_user_data(target.id, target.full_name)
    t_user["warns"] = 0
    await message.reply(f"✅ {get_mention(target)}ning barcha ogohlantirishlari kechirildi va nolga tushirildi.", parse_mode="Markdown")

@dp.message(Command("ban"))
async def ban_user(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    try:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=target.id)
        await message.reply(f"✈️ {get_mention(target)} guruhdan butunlay haydab yuborildi (Ban).", parse_mode="Markdown")
    except:
        await message.reply("Ban qilishda xatolik.")

@dp.message(Command("unban"))
async def unban_user(message: types.Message):
    if not await check_is_admin(message): return
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    try:
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=target.id, only_if_banned=True)
        await message.reply(f"🔓 {get_mention(target)} qora ro'yxatdan chiqarildi.", parse_mode="Markdown")
    except:
        await message.reply("Xatolik yuz berdi.")

@dp.message(Command("del"))
async def delete_messages(message: types.Message):
    if not (await check_is_admin(message) or await check_is_admin(message, "mod")): return
    if not message.reply_to_message: return
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except: pass

@dp.message(Command("night"))
async def set_night_mode(message: types.Message):
    if not await check_is_admin(message): return
    group_status["mode"] = "night"
    await message.reply("🌃 **Tungi rejim yoqildi!** \nGuruh qulflandi. Adminlardan tashqari barcha a'zolar mut qilindi. Mafiya guruhda ovozsiz o'yin boshlaydi! 🤫")

@dp.message(Command("day"))
async def set_day_mode(message: types.Message):
    if not await check_is_admin(message): return
    group_status["mode"] = "day"
    await message.reply("☀️ **Kunduzgi rejim yoqildi!** \nGuruh ochildi. Hamma gapirishi va o'yinni guruhda qizg'in muhokama qilishi mumkin! 🗣")
@dp.message(Command("info"))
async def user_info(message: types.Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    u = get_user_data(target.id, target.full_name)
    text = f"📝 **Foydalanuvchi kartochkasi**\n\n👤 **Nik:** {get_mention(target)}\n🆔 **ID:** `{u['id']}`\n📅 **Kirgan sana:** {u['joined']}\n💬 **Xabarlari:** {u['messages']} ta\n⚠️ **Ogohlantirishlar:** {u['warns']}/3\n🎖 **Unvoni:** {u['role']}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔇 1 soat mut", callback_data=f"inline_mute_{target.id}"), InlineKeyboardButton(text="🔊 Mutdan chiqarish", callback_data=f"inline_unmute_{target.id}")]])
    await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("inline_"))
async def inline_buttons_handler(callback: CallbackQuery):
    is_admin = False
    if callback.message.sender_chat and callback.message.sender_chat.id == callback.message.chat.id:
        is_admin = True
    else:
        u = get_user_data(callback.from_user.id)
        if u["rights"]["is_admin"] or u["rights"]["is_main"]:
            is_admin = True
    if not is_admin:
        return await callback.answer("Siz guruh admini emassiz!", show_alert=True)
        
    data_parts = callback.data.split("_")
    action = data_parts[1]
    target_id = int(data_parts[2])
    
    if action == "mute":
        until = int(time.time() + 3600)
        try:
            await bot.restrict_chat_member(chat_id=callback.message.chat.id, user_id=target_id, permissions=types.ChatPermissions(can_send_messages=False), until_date=until)
            await callback.answer("Foydalanuvchi 1 soatga mut qilindi!", show_alert=True)
        except:
            await callback.answer("Xatolik: Huquq yetarli emas.")
    elif action == "unmute":
        try:
            await bot.restrict_chat_member(chat_id=callback.message.chat.id, user_id=target_id, permissions=types.ChatPermissions(can_send_messages=True))
            await callback.answer("Foydalanuvchi mutdan chiqarildi!", show_alert=True)
        except:
            await callback.answer("Xatolik yuz berdi.")

@dp.message(Command("crush"))
async def crush_game(message: types.Message):
    if not message.reply_to_message: return await message.reply("Ushbu buyruqni biror a'zoning xabariga reply qilib yozing! ❤️")
    sender, target = message.from_user, message.reply_to_message.from_user
    love_messages = [f"❤️ Oho! {get_mention(sender)} guruhda hamma oldida {get_mention(target)}ga sevgi izhor qildi! Yuraklar yonmoqda! 😍", f"💖 {get_mention(sender)} tunu-kun {get_mention(target)} haqida o'ylayotganini va unga telbalarcha oshiq bo'lganini tan oldi! ✨", f"💘 Tasodifni qarang! {get_mention(sender)} va {get_mention(target)} bir-birlari uchun yaratilgan! Baxtli bo'linglar! 🌸"]
    await message.reply(random.choice(love_messages), parse_mode="Markdown")

@dp.message(Command("shoot"))
async def shoot_game(message: types.Message):
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    await message.reply(f"🕵️‍♂️ **Mafiya Doni buyrug'iga ko'ra:** Guruhda o'q ovozi eshitildi! {get_mention(target)}ga ovozsiz o'q tegdi... 💀", parse_mode="Markdown")

@dp.message(Command("check"))
async def check_game(message: types.Message):
    if not message.reply_to_message: return
    target = message.reply_to_message.from_user
    roles = ["🔴 Qizil mafiya", "⚪️ Oq fuqaro", "🩺 Shifokor", "🕶 Don (Mafiya boshlig'i)", "🕵️‍♂️ Komissar Detektiv"]
    chosen_role = random.choice(roles)
    await message.reply(f"🔎 **Komissar Detektiv** tunda tekshiruv o'tkazdi...\n🕵️‍♂️ {get_mention(target)} tekshirildi va uning roli: **{chosen_role}**", parse_mode="Markdown")

@dp.message(Command("channels"))
async def official_channels(message: types.Message):
    text = "📢 **mafia_uzbekis klubining rasmiy loyihalari:**\n\n🔹 [Klubning Rasmiy Kanali](https://t.me)\n📜 [Klub Qoidalari](https://t.me_rules)\n📸 [Zapallar Kanali](https://t.me_zapallar)"
    await message.reply(text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message(Command("help"))
async def help_command(message: types.Message):
    text = "🤖 **Botdagi barcha asosiy buyruqlar ro'yxati:**\n\n👑 **Ega huquqlari:**\n/main, /unmain - Oliy adminlikni boshqarish\n\n🛠 **Admin huquqlari:**\n/admin, /unadmin - Guruh admini qilish/olish\n/moderator, /unmoderator - Moderatorlik\n/muter, /unmuter - Faqat mut qilish huquqi\n\n⚖️ **Moderatsiya (Reply):**\n/mute [vaqt] [sabab] - Ovozni o'chirish\n/unmute - Blokdan chiqarish\n/warn, /unwarn - Ogohlantirish berish/nol qilish\n/ban, /unban - Guruhdan haydash va chiqarish\n/del - Xabarlarni o'chirish\n\n🌆 **Guruh Nazorati:**\n/night, /day - Tungi/Kunduzgi rejim\n\n🎉 **Ko'ngilochar (Hamma uchun):**\n/info - Foydalanuvchi kartochkasi\n/crush - Sevgi izhori ssenariysi\n/shoot - O'q uzish ssenariysi\n/check - Komissar tekshiruvi\n/channels - Rasmiy loyihalar"
    await message.reply(text, parse_mode="Markdown")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True)
    yield
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root(): return {"status": "alive"}

@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    update_json = await request.json()
    update = types.Update.model_validate(update_json, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
