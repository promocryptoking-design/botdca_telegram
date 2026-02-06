import math
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =============================
# CONFIGURACIÓN
# =============================
BOT_TOKEN = "8411801238:AAE7Dx971g9iD7-sV8aV3iIXG61PIPBf7Bc"
GRUPO_ID_PERMITIDO = -1002932339573  # Academia CK
MAX_DCA = 25

# =============================
# UTILIDADES
# =============================
async def es_miembro_grupo(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(GRUPO_ID_PERMITIDO, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def reset_state(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()


# =============================
# /start
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await es_miembro_grupo(user_id, context):
        await update.message.reply_text(
            "⛔ Acceso restringido.\n\n"
            "Esta herramienta es exclusiva para miembros del grupo *Academia CK*.",
            parse_mode="Markdown",
        )
        return

    reset_state(context)
    context.user_data["step"] = "usdt"

    await update.message.reply_text(
        "✅ *Acceso concedido*\n\n"
        "Vamos paso a paso.\n\n"
        "💱 *Paso 1*\n"
        "Ingresa la cantidad de **USDT** que deseas convertir a BTC:",
        parse_mode="Markdown",
    )


# =============================
# MANEJO DE MENSAJES
# =============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    try:
        value = float(text)
    except:
        await update.message.reply_text("❌ Ingresa un número válido.")
        return

    # -------- CONVERSOR --------
    if step == "usdt":
        context.user_data["usdt"] = value
        context.user_data["step"] = "btc_price"
        await update.message.reply_text("Precio actual de BTC:")
        return

    if step == "btc_price":
        usdt = context.user_data["usdt"]
        btc = usdt / value
        context.user_data["btc_capital"] = btc

        context.user_data["step"] = "btc_total"
        await update.message.reply_text(
            f"💰 BTC equivalente: *{btc:.6f} BTC*\n\n"
            "👉 Este valor se usará como capital inicial.\n\n"
            "Ingresa el **BTC total (spot)**:",
            parse_mode="Markdown",
        )
        return

    # -------- CAPITAL --------
    if step == "btc_total":
        context.user_data["btc_total"] = value
        context.user_data["step"] = "price_entry"
        await update.message.reply_text("Precio BTC de entrada:")
        return

    if step == "price_entry":
        context.user_data["price"] = value
        context.user_data["step"] = "collateral"
        await update.message.reply_text("% de BTC usado como colateral:")
        return

    if step == "collateral":
        context.user_data["collateral"] = value / 100
        context.user_data["step"] = "leverage"
        await update.message.reply_text("Apalancamiento (ej: 5):")
        return

    if step == "leverage":
        context.user_data["lev"] = value
        context.user_data["step"] = "entry"
        await update.message.reply_text("% entrada inicial:")
        return

    if step == "entry":
        context.user_data["entry"] = value / 100
        context.user_data["step"] = "dca"
        await update.message.reply_text("% DCA por nivel:")
        return

    if step == "dca":
        context.user_data["dca"] = value / 100
        context.user_data["step"] = "dca_count"
        await update.message.reply_text(
            f"Número de niveles DCA (máx {MAX_DCA}):"
        )
        return

    if step == "dca_count":
        if value > MAX_DCA:
            await update.message.reply_text(
                f"⚠️ Máximo permitido: {MAX_DCA} niveles."
            )
            return
        context.user_data["dca_count"] = int(value)
        context.user_data["step"] = "step_dist"
        await update.message.reply_text("Distancia entre DCAs (%):")
        return

    if step == "step_dist":
        context.user_data["step_dist"] = value / 100
        context.user_data["step"] = "target"
        await update.message.reply_text("Precio objetivo BTC:")
        return

    if step == "target":
        context.user_data["target"] = value
        context.user_data["step"] = "days"
        await update.message.reply_text("Duración del trade (días):")
        return

    if step == "days":
        context.user_data["days"] = value
        await calcular(update, context)


# =============================
# CÁLCULO PRINCIPAL
# =============================
async def calcular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data

    btc = d["btc_total"]
    price = d["price"]
    col = btc * d["collateral"]
    lev = d["lev"]
    entry = d["entry"]
    dca = d["dca"]
    n = d["dca_count"]
    step = d["step_dist"]
    target = d["target"]
    days = d["days"]

    prices = []
    sizes = []
    margins = []
    used = 0

    for i in range(n + 1):
        m = col * (entry if i == 0 else dca)
        if used + m > col:
            break
        p = price * ((1 - step) ** i)
        prices.append(p)
        sizes.append(m * lev)
        margins.append(m)
        used += m

    size_total = sum(sizes)
    avg = sum(prices[i] * sizes[i] for i in range(len(sizes))) / size_total

    free = col - used
    liq = avg * (1 - free / size_total)
    risk = (price - liq) / price * 100

    pnl_bruto = size_total * ((target - avg) / avg)
    fees = size_total * 0.00025 * 2
    funding = size_total * 0.0001 * (days * 3)
    pnl_neto = pnl_bruto - fees - funding

    btc_final = btc + pnl_neto

    # -------- RESUMEN --------
    await update.message.reply_text(
        f"📊 *RESULTADO GENERAL*\n\n"
        f"Precio promedio: `{avg:.0f}`\n"
        f"Liquidación: `{liq:.0f}`\n"
        f"Riesgo: `{risk:.1f}%`\n\n"
        f"PnL neto futuros: `{pnl_neto:.4f} BTC`\n"
        f"Valor final sistema: `${btc_final * target:,.0f}`\n\n"
        f"Solo spot: `${btc * target:,.0f}`\n"
        f"Diferencia: `${(btc_final - btc) * target:,.0f}`",
        parse_mode="Markdown",
    )

    # -------- DETALLE POR NIVELES --------
    msg = "📋 *DETALLE DCA*\n\n"
    btc_acc = 0

    for i in range(len(prices)):
        btc_acc += sizes[i]
        avg_i = sum(prices[j] * sizes[j] for j in range(i + 1)) / sum(sizes[: i + 1])
        gain = (target - avg_i) * btc_acc

        msg += (
            f"Nivel {i}\n"
            f"Precio: {prices[i]:.0f}\n"
            f"Nocional BTC: {btc_acc:.4f}\n"
            f"Ganancia estimada: ${gain:,.0f}\n\n"
        )

        if i % 5 == 4:
            await update.message.reply_text(msg, parse_mode="Markdown")
            msg = ""

    if msg:
        await update.message.reply_text(msg, parse_mode="Markdown")

    reset_state(context)


# =============================
# MAIN
# =============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 AlertasTradingVip_bot activo")
    app.run_polling()


if __name__ == "__main__":
    main()
