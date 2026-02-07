import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))  # ej: -1002932339573

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =====================
# HELPERS
# =====================
async def is_allowed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.id != GROUP_ID:
        await update.message.reply_text("⛔ Este bot solo funciona dentro del grupo Academia CK.")
        return False
    return True

# =====================
# COMMANDS
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update, context):
        return

    await update.message.reply_text(
        "📊 *Calculadora BTC DCA*\n\n"
        "Usa el comando:\n"
        "`/dca capital precio niveles porcentaje`\n\n"
        "Ejemplo:\n"
        "`/dca 500 80000 10 2`",
        parse_mode="Markdown"
    )

async def dca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update, context):
        return

    try:
        capital = float(context.args[0])
        precio = float(context.args[1])
        niveles = int(context.args[2])
        porcentaje = float(context.args[3])

        if niveles > 25:
            await update.message.reply_text("⚠️ Máximo permitido: 25 niveles DCA.")
            return

        mensaje = f"📉 *BTC DCA*\n\nCapital: {capital} USDT\nPrecio inicial: {precio}\n\n"
        precio_actual = precio

        for i in range(1, niveles + 1):
            mensaje += f"Nivel {i}: {precio_actual:.2f}\n"
            precio_actual *= (1 - porcentaje / 100)

        await update.message.reply_text(mensaje, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text(
            "❌ Error en los parámetros.\n"
            "Uso correcto:\n"
            "`/dca capital precio niveles porcentaje`",
            parse_mode="Markdown"
        )

# =====================
# MAIN
# =====================
def main():
    print("🚀 AlertasTradingVip_bot iniciando...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dca", dca))

    app.run_polling()

if __name__ == "__main__":
    main()

