import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# =========================
# UTILIDAD: verificar miembro
# =========================
async def is_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False


# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id

    if not await is_member(user_id, context):
        await update.message.reply_text(
            "🚫 Acceso restringido\n\n"
            "Este bot es exclusivo para miembros del grupo *Academia CK*."
        )
        return

    await update.message.reply_text(
        "✅ Acceso confirmado\n\n"
        "Comandos disponibles:\n"
        "/dca → Calculadora BTC DCA\n"
        "/help → Ayuda"
    )


# =========================
# /help
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id

    if not await is_member(user_id, context):
        await update.message.reply_text("🚫 No tienes acceso.")
        return

    await update.message.reply_text(
        "📘 *Ayuda – Academia CK*\n\n"
        "/dca → Ejecutar calculadora DCA\n"
        "El bot funciona solo en privado."
    )


# =========================
# /dca (placeholder)
# =========================
async def dca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id

    if not await is_member(user_id, context):
        await update.message.reply_text("🚫 Acceso denegado.")
        return

    # AQUÍ luego va tu lógica DCA completa
    await update.message.reply_text(
        "📊 *Calculadora BTC DCA*\n\n"
        "Aquí irá la calculadora completa.\n"
        "Acceso exclusivo confirmado ✅"
    )


# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("dca", dca))

    print("🤖 AlertasTradingVip_bot iniciado correctamente")
    app.run_polling()


if __name__ == "__main__":
    main()
