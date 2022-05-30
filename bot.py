import logging
import requests
import validators
import time
import os
from pyqrcode import QRCode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update

TOKEN = "5348460983:AAGdpwSEinQkWGF6K_UJH8DfSACZcHY1ASk"
KEY = "sk_lCHibSOLAdIqyJUZ"
admins = [839574311]   

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

start_msg = '''
<b>PTUTM Link Shortener</b>✨
<i>Sent your link below!👇</i>
_______________________
<b>@DMT-PTUTM</b>
'''

help_msg = '''
<b>Sent a valid link to start.</b>
<i>Contact</i> <u>@DMT-PTUTM</u> <i>for custom path name.</i>
'''

def start(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id in admins:
        update.message.reply_html(start_msg)
    else:
        update.message.reply_html('''<b>You are NOT AUTHORIZED to use this bot</b>

To access, contact <i>@DMT-PTUTM</i>''')
    
def help_command(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id in admins:
        update.message.reply_html(help_msg)
    else:
        update.message.reply_html('''<b>You are NOT AUTHORIZED to use this bot</b>

To access, contact <i>@DMT-PTUTM</i>''')

def msg(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id in admins:
        long_URL = update.message.text
        message_id = update.message.message_id
        valid = validators.url(long_URL)

        if valid != True:
            update.message.reply_html("❌ <b>Invalid link</b> ❌ \nResend a valid link below!")
            return msg

        delete = update.message.reply_text("⏳ Generating...",reply_to_message_id=message_id)

        url = "https://api.short.io/links"
        payload = {
            "allowDuplicates": False,
            "domain": "ptutm.tk",
            "originalURL": long_URL
        }        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": KEY
        }
        response = requests.post(url, json=payload, headers=headers)
        short_URL = response.json()['shortURL']
        path = response.json()['path']

        qr_file = f'PTUTM-{path}.png'
        Qr_Code = QRCode(long_URL)
        Qr_Code.png(qr_file, scale=20)
        update.message.reply_document(document=open(qr_file, "rb"),caption='''Here is the shortened link:
    ------------------------------------------
    👉 {}
    ------------------------------------------
    @DMT-PTUTM'''.format(short_URL))
        os.remove(qr_file)

        context.bot.editMessageText(chat_id=update.message.chat_id,message_id=delete.message_id, text="✅ SUCCESS !")
        time.sleep(5)
        context.bot.deleteMessage (message_id = delete.message_id,chat_id = update.message.chat_id)

    else:
        update.message.reply_html('''<b>You are NOT AUTHORIZED to use this bot</b>

To access, contact <i>@DMT-PTUTM</i>''')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, msg))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()