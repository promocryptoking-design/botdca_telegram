import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# --------- HELPERS ---------

async def is_user_in_group(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --------- COMMANDS ---------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_user_in_group(context, user.id):
        await update.message.reply_text(
            "⛔ Acceso denegado\n\n"
            "Esta calculadora es exclusiva para miembros de *Academia CK*.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "✅ *Acceso concedido*\n\n"
        "Bienvenido a la *Calculadora BTC DCA*\n\n"
        "Usa /dca para iniciar el cálculo.",
        parse_mode="Markdown"
    )

async def dca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *Calculadora BTC DCA*\n\n"
        "⚠️ Máximo permitido: *25 niveles DCA*\n\n"
        "👉 (Aquí continúa el flujo paso a paso)",
        parse_mode="Markdown"
    )

# --------- MAIN ---------

def main():
    print("🤖 AlertasTradingVip_bot iniciando...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dca", dca))

    app.run_polling()

if __name__ == "__main__":
    main()
