import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002932339573  # Academia CK

# ---------- UTIL ----------
async def check_group(update: Update) -> bool:
    if update.effective_chat.id != GROUP_ID:
        await update.message.reply_text(
            "⛔ Acceso restringido.\n"
            "Esta calculadora es exclusiva de la Academia CK."
        )
        return False
    return True

# ---------- COMANDOS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group(update):
        return

    await update.message.reply_text(
        "📊 *Calculadora BTC DCA*\n\n"
        "Comandos disponibles:\n"
        "/usdtbtc <usdt> <precio>\n"
        "/dca <capital_usdt> <precio_inicial> <niveles>\n\n"
        "⚠️ Máximo 25 niveles DCA",
        parse_mode="Markdown"
    )

async def usdt_btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group(update):
        return

    try:
        usdt = float(context.args[0])
        precio = float(context.args[1])
        btc = usdt / precio

        await update.message.reply_text(
            f"🔄 *USDT → BTC*\n\n"
            f"Inversión: `{usdt}` USDT\n"
            f"Precio BTC: `{precio}`\n\n"
            f"➡️ Resultado: `{btc:.6f} BTC`",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text(
            "❌ Uso correcto:\n/usdtbtc 500 80000"
        )

async def dca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group(update):
        return

    try:
        capital = float(context.args[0])
        precio = float(context.args[1])
        niveles = int(context.args[2])

        if niveles > 25:
            await update.message.reply_text(
                "⚠️ Máximo permitido: 25 niveles DCA"
            )
            return

        msg = "📉 *Estrategia DCA BTC*\n\n"
        drop = 0.02

        for i in range(1, niveles + 1):
            precio_nivel = precio * (1 - drop * i)
            msg += f"Nivel {i}: `{precio_nivel:.2f}`\n"

        msg += "\n⚠️ No se aceptan más de 25 niveles DCA."

        await update.message.reply_text(msg, parse_mode="Markdown")

    except:
        await update.message.reply_text(
            "❌ Uso correcto:\n/dca 1000 80000 10"
        )

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("usdtbtc", usdt_btc))
    app.add_handler(CommandHandler("dca", dca))

    print("🤖 AlertasTradingVip_bot iniciado")
    app.run_polling()

if __name__ == "__main__":
    main()

