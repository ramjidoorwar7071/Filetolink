import os
from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from threading import Thread

# ✅ Aapka real bot token
TELEGRAM_BOT_TOKEN = "7492936947:AAHnynRFwUsRyz7tbncm7zP0BjR59_GJkzI"

# ✅ Uploads folder banega yahan
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Flask app start karega server
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return "🤖 Bot is Running!"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ✅ Telegram bot file receive karega
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Please send a valid file.")
        return

    file = await context.bot.get_file(document.file_id)
    filename = document.file_name
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    await file.download_to_drive(filepath)

    # ✅ Public download link (👇 Render.com URL yahan daalo)
    public_url = f"https://your-app-name.onrender.com/uploads/{filename}"

    await update.message.reply_text(
        f"✅ File uploaded successfully!\n📥 Download link:\n{public_url}"
    )

# ✅ Telegram bot start function
def run_bot():
    app_telegram = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app_telegram.run_polling()

# ✅ Flask + Telegram parallel run
if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
