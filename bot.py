from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import config
from database import save_user, save_request

# ================= STATES =================
LANG, CONTACT, LOCATION, PHOTO, MENU = range(5)

# ================= TEXTS =================
TEXTS = {
    "uz": {
        "contact": "📞 Telefon raqamingizni yuboring:",
        "contact_saved": "✅ Rahmat! Kontakt qabul qilindi.",
        "location": "📍 Lokatsiya yuboring:",
        "photo": "📸 Manzilni aniq topib borishimiz uchun atrof muhitni ko‘rsatadigan rasm yuboring.",
        "done": "✅ Ma'lumotlar qabul qilindi!",
        "menu": "💼 Xizmatni tanlang:",
        "final": "📩 So'rovingiz qabul qilindi!\n👨‍💼 Tez orada operator bog‘lanadi.",
        "operator": "👨‍💼 Operator: Ayubalikhan\n📞 +998 (90) 935 11 77",
        "consultation": "📝 Bepul konsultatsiya va loyihani hisoblash so‘rovingiz qabul qilindi!",
        "calculation": "📐 Butun obyekt bo‘yicha bepul hisob-kitob so‘rovingiz qabul qilindi!",
        "restart": "🔄 Yangidan boshlash"
    },
    "ru": {
        "contact": "📞 Отправьте номер телефона:",
        "contact_saved": "✅ Контакт сохранен.",
        "location": "📍 Отправьте локацию:",
        "photo": "📸 Чтобы мы могли точно найти адрес, отправьте фото окружающей местности.",
        "done": "✅ Данные получены!",
        "menu": "💼 Выберите услугу:",
        "final": "📩 Ваша заявка принята!\n👨‍💼 Оператор свяжется с вами.",
        "operator": "👨‍💼 Оператор: Ayubalikhan\n📞 +998 (90) 935 11 77",
        "consultation": "📝 Запрос на бесплатную консультацию и расчет проекта принят!",
        "calculation": "📐 Запрос на бесплатный расчет по всему объекту принят!",
        "restart": "🔄 Начать заново"
    },
    "en": {
        "contact": "📞 Send your phone number:",
        "contact_saved": "✅ Contact saved.",
        "location": "📍 Send location:",
        "photo": "📸 Send a photo of the surrounding area to help us find your location accurately.",
        "done": "✅ Data received!",
        "menu": "💼 Choose service:",
        "final": "📩 Your request has been received!\n👨‍💼 Our operator will contact you soon.",
        "operator": "👨‍💼 Operator: Ayubalikhan\n📞 +998 (90) 935 11 77",
        "consultation": "📝 Free consultation and project calculation request received!",
        "calculation": "📐 Free full-object calculation request received!",
        "restart": "🔄 Restart"
    }
}

MENU_BUTTONS = {
    "uz": [
        ["📊 Menga bepul konsultatsiya va loyihani hisoblash kerak"],
        ["🏗 Menga butun obyekt bo‘yicha bepul hisob-kitob kerak"],
        ["🎨 Menda tayyor <3D dizayn> bor"],
        ["🎨 Menga dizayner xizmati (2D/3D) kerak"],
        ["📞 Operator bilan bog'lanish"]
    ],
    "ru": [
        ["📊 Мне нужна бесплатная консультация и расчет проекта"],
        ["🏗 Мне нужен бесплатный расчет по всему объекту"],
        ["🎨 У меня есть готовый <3D дизайн>"],
        ["🎨 Мне нужны услуги дизайнера (2D/3D)"],
        ["📞 Связаться с оператором"]
    ],
    "en": [
        ["📊 I need free consultation and project calculation"],
        ["🏗 I need free full-object calculation"],
        ["🎨 I have a ready <3D design>"],
        ["🎨 I need designer service (2D/3D)"],
        ["📞 Contact operator"]
    ]
}

CONTACT_BUTTONS = {
    "uz": "📞 Telefon raqam yuborish",
    "ru": "📞 Отправить номер",
    "en": "📞 Send phone number"
}

LOCATION_BUTTONS = {
    "uz": "📍 Lokatsiya yuborish",
    "ru": "📍 Отправить локацию",
    "en": "📍 Send location"
}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    keyboard = [["🇬🇧 English", "🇷🇺 Русский", "🇺🇿 O'zbek"]]
    await update.message.reply_text(
        "🌐 Tilni tanlang / Choose language / Выберите язык",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return LANG


# ================= CANCEL =================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Jarayon bekor qilindi. /start orqali qayta boshlang.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ================= LANGUAGE =================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "O'zbek" in text:
        lang = "uz"
    elif "Русский" in text:
        lang = "ru"
    else:
        lang = "en"

    context.user_data["lang"] = lang
    context.user_data["user_id"] = update.effective_user.id

    keyboard = [
        [KeyboardButton(CONTACT_BUTTONS[lang], request_contact=True)],
        [TEXTS[lang]["restart"]]
    ]

    await update.message.reply_text(
        TEXTS[lang]["contact"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CONTACT


# ================= CONTACT =================
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["lang"]

    if update.message.text == TEXTS[lang]["restart"]:
        return await start(update, context)

    if update.message.contact:
        context.user_data["contact"] = update.message.contact.phone_number
        await update.message.reply_text(TEXTS[lang]["contact_saved"])
    else:
        return CONTACT

    keyboard = [
        [KeyboardButton(LOCATION_BUTTONS[lang], request_location=True)],
        [TEXTS[lang]["restart"]]
    ]

    await update.message.reply_text(
        TEXTS[lang]["location"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return LOCATION


# ================= LOCATION =================
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["lang"]

    if update.message.text == TEXTS[lang]["restart"]:
        return await start(update, context)

    if update.message.location:
        loc = update.message.location
        context.user_data["lat"] = loc.latitude
        context.user_data["lon"] = loc.longitude

        await update.message.reply_text(
            TEXTS[lang]["photo"],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]["restart"]]], resize_keyboard=True)
        )
        return PHOTO

    return LOCATION


# ================= PHOTO =================
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["lang"]

    if update.message.text == TEXTS[lang]["restart"]:
        return await start(update, context)

    user_data = {
        "user_id": context.user_data["user_id"],
        "lang": lang,
        "contact": context.user_data["contact"],
        "lat": context.user_data["lat"],
        "lon": context.user_data["lon"]
    }

    save_user(user_data)

    await context.bot.send_message(
        chat_id=config.ADMIN_ID,
        text=f"🆕 Yangi user\nID: {user_data['user_id']}\nTel: {user_data['contact']}\nLokatsiya: {user_data['lat']}, {user_data['lon']}\nTil: {lang}"
    )

    keyboard = MENU_BUTTONS[lang] + [[TEXTS[lang]["restart"]]]

    await update.message.reply_text(
        TEXTS[lang]["menu"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MENU


# ================= MENU =================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data["lang"]
    text = update.message.text
    user_id = update.effective_user.id

    if text == TEXTS[lang]["restart"]:
        return await start(update, context)

    buttons = MENU_BUTTONS[lang]

    if text == buttons[4][0]:
        await update.message.reply_text(TEXTS[lang]["operator"])
        return MENU

    save_request(user_id, text, lang)

    await context.bot.send_message(
        config.ADMIN_ID,
        f"📩 Yangi so‘rov\nUser: {user_id}\nXizmat: {text}"
    )

    await update.message.reply_text(TEXTS[lang]["final"])
    return MENU


# ================= APP =================
def get_app():
    app = ApplicationBuilder().token(config.TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT, set_language)],
            CONTACT: [MessageHandler(filters.ALL, get_contact)],
            LOCATION: [MessageHandler(filters.ALL, get_location)],
            PHOTO: [MessageHandler(filters.ALL, get_photo)],
            MENU: [MessageHandler(filters.TEXT, menu_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("cancel", cancel))

    return app