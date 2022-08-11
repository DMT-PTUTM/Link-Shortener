import logging
from secrets import choice
import requests
import validators
import time
import os
from pyqrcode import QRCode
from telegram.ext import *
from telegram import *

TOKEN = "TELEGRAM_BOT_TOKEN"
KEY = "SHORT.IO_API_KEY"

CHOICE, PATH, SHORTEN, QR = range(4)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

help_msg= '''
<b>点击 /start 开始</b>
<b>点击 /cancel 取消</b>
<i>若有任何疑问请联系</i> <u>@DMT-PTUTM</u>
'''
start_msg = '''
<b>✨PTUTM Link Shortener</b>✨

<b><u>版本更新 2.0.1:</u></b> 
<i>- 支持自定义网站路径</i>
<i>- 授权模式: 只限PTUTM筹委使用</i>
<i>- 现已支持中文版</i>
_______________________
<b>©PTUTM-DMT</b>
'''

askpath_msg = '''<u>是否需要自定义网络路径❓</u>

若选择 <b>Yes</b>, 可自定义链接后尾的字
例子: cny2022
新链接: https://ptutm.tk/cny2022

若选择 <b>No</b>, 系统将自定义网络路径
新链接: https://ptutm.tk/1X4y
'''

choice_msg = '''请输入自定义网络路径:
注: 不能空格, 可以underscore或(-)

例子：
1. cny2022 ✅
2. cny_2022 ✅
3. cny 2022 ❌'''

def help_command(update: Update, context: CallbackContext) -> None:
        update.message.reply_html(help_msg)

def start_command(update: Update, context: CallbackContext) -> None:

    update.message.reply_html(start_msg)
    keyboard = [[InlineKeyboardButton("Yes",callback_data='Yes')],[InlineKeyboardButton("No",callback_data='No')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html(askpath_msg, reply_markup=reply_markup)
    return CHOICE

def choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer
    choice = query.data
    context.user_data['choice'] = choice
    if choice == "Yes":
        update.callback_query.message.reply_html(choice_msg)
        return PATH
    if choice == 'No':
        update.callback_query.message.reply_html("Okay, 系统将自定义网络路径. \n\n<b>请输入要缩短的链接:</b>")
        return SHORTEN

def path(update: Update, context: CallbackContext) -> None:
    path = update.message.text
    context.user_data['path'] = path
    update.message.reply_html("Okay, 你输入的路径为 <b>\"{}\"</b> \n\n<b>请输入要缩短的链接:</b>".format(path))
    return SHORTEN

def shorten(update: Update, context: CallbackContext) -> None:
    choice = context.user_data['choice']
    long_URL = update.message.text
    message_id = update.message.message_id
    valid = validators.url(long_URL)

    if valid != True:
        update.message.reply_html("❌ <b>无效链接</b> ❌ \n请重新输入你的链接\n例子：https://google.com\n点击 /cancel 返回起点.")
        return SHORTEN

    delete = update.message.reply_text("⏳ 正在生成链接...",reply_to_message_id=message_id)

    if choice == 'Yes':
        path = context.user_data['path']
        url = "https://api.short.io/links"
        payload = {
            "allowDuplicates": False,
            "domain": "ptutm.tk",
            "originalURL": long_URL,
            "path": path
        }        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": KEY
        }

    if choice == 'No':
        url = "https://api.short.io/links"
        payload = {
            "allowDuplicates": False,
            "domain": "ptutm.tk",
            "originalURL": long_URL,
        }        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": KEY
        }

    response = requests.post(url, json=payload, headers=headers)
    short_URL = response.json()['shortURL']
    path = response.json()['path']
    context.user_data['short_URL'] = short_URL
    context.user_data['path'] = path

    keyboard = [[InlineKeyboardButton("Qr Code",callback_data='1')],[InlineKeyboardButton("重新开始",callback_data='2')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html('''以下是已缩短的链接:
------------------------------------------
👉 {}
------------------------------------------
©PTUTM-DMT

点击 /start 返回起点'''.format(short_URL),disable_web_page_preview=True,reply_markup=reply_markup)

    context.bot.editMessageText(chat_id=update.message.chat_id,message_id=delete.message_id, text="✅ 成功 !")
    time.sleep(5)
    context.bot.deleteMessage (message_id = delete.message_id,chat_id = update.message.chat_id)
    return QR

def qr(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    choice = query.data
    if choice == '1':
        short_URL = context.user_data['short_URL']
        path = context.user_data['path']
        qr_file = f'PTUTM-{path}.png'
        Qr_Code = QRCode(short_URL)
        Qr_Code.png(qr_file, scale=20)
        update.callback_query.message.reply_document(document=open(qr_file, "rb"))
        os.remove(qr_file)
        update.callback_query.message.reply_text("点击 /start 重新开始")
        return ConversationHandler.END
    if choice == '2':
        update.callback_query.message.reply_text("点击 /start 重新开始")
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_html("你取消了这个程序.\n<b>点击 /start 重新开始</b>")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            CHOICE: [CallbackQueryHandler(choice)],
            PATH: [MessageHandler(filters=~Filters.command,callback=path)],
            SHORTEN: [MessageHandler(filters=~Filters.command,callback=shorten)],
            QR: [CallbackQueryHandler(qr)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
