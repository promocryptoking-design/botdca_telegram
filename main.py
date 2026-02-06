import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id != GROUP_ID and update.effective_chat.type != "private":
        return

    await update.message.reply_text(
        "🤖 *AlertasTradingVip_bot activo*\n\n"
        "Este bot es exclusivo para la *Academia CK*.\n\n"
        "Comandos disponibles:\n"
        "/dca → Calculadora BTC DCA",
        parse_mode="Markdown"
    )

async def dca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id != GROUP_ID:
        await update.message.reply_text(
            "❌ Acceso denegado.\nEste comando solo funciona en el grupo oficial."
        )
        return

    await update.message.reply_text(
        "📊 *Calculadora BTC DCA*\n\n"
        "✔ Conversión USDT → BTC\n"
        "✔ Gestión de capital\n"
        "✔ Hasta *25 niveles DCA*\n\n"
        "⚠️ No se aceptan más de 25 recompras.",
        parse_mode="Markdown"
    )

# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN no definido")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dca", dca))

    print("🤖 AlertasTradingVip_bot iniciado correctamente")
    app.run_polling()

if __name__ == "__main__":
    main()
