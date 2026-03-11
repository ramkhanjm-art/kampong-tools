import os
import asyncio
import io
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rembg import remove
from PIL import Image
import segno
import edge_tts
import yt_dlp
from groq import Groq
from deep_translator import GoogleTranslator

# --- លាក់ API and token ដោយប្រើ os.getenv ---
# វានឹងទៅទាញយកតម្លៃពី Environment Variables ដែលយើងបានកំណត់ក្នុង Render ឬក្នុងកុំព្យូទ័រ
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API = os.getenv("GROQ_API_KEY")

# កំណត់ Menu
MENU = [['លុប Background', 'Text to Speech'], ['បង្កើត QR Code', 'បកប្រែ'], ['AI Assistant', 'ជំនួយ']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    await update.message.reply_text("សួស្ដី! ខ្ញុំជា Bot ជំនួយការឆ្លាតវៃ។ សូមរើស Tool ខាងក្រោម៖", reply_markup=reply_markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ កំពុងលុប Background...")
    photo_file = await update.message.photo[-1].get_file()
    img_bytes = await photo_file.download_as_bytearray()
    
    input_img = Image.open(io.BytesIO(img_bytes))
    output_img = remove(input_img)
    
    out_io = io.BytesIO()
    output_img.save(out_io, 'PNG')
    out_io.seek(0)
    
    await update.message.reply_document(document=out_io, filename="no_bg.png")
    await status_msg.delete()

async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("សូមវាយ: /tts អត្ថបទដែលអ្នកចង់ឱ្យនិយាយ")
        return
    
    communicate = edge_tts.Communicate(text, "km-KH-SreymomNeural")
    out_io = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            out_io.write(chunk["data"])
    out_io.seek(0)
    await update.message.reply_voice(voice=out_io)

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GROQ_API:
        await update.message.reply_text("Error: GROQ_API_KEY មិនទាន់បានដំឡើង។")
        return
        
    user_msg = update.message.text
    client = Groq(api_key=GROQ_API)
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_msg}]
    )
    await update.message.reply_text(chat.choices[0].message.content)

def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN មិនត្រូវបានរកឃើញក្នុង Environment Variables ទេ។")
        return

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tts", tts))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
