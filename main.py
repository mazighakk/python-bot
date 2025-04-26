import requests
import json
import time
import telebot
import re
import os
from datetime import datetime, timedelta

# إعدادات البوت

def load_user_data():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_user_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=2)

def hide_phone_number(number):
    return f"{number[:5]}****{number[-2:]}"
TOKEN = '8016863611:AAG3CoXHIsw_XfwmSN-Z8pXp_D1IK5YDAZ4'
bot = telebot.TeleBot(TOKEN)

# إرسال OTP
def send_otp(msisdn):
    url = 'https://apim.djezzy.dz/oauth2/registration'
    payload = f'msisdn={msisdn}&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&scope=smsotp'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    try:
        response = requests.post(url, data=payload, headers=headers, verify=False)
        return response.status_code == 200
    except:
        return False

# التحقق من OTP
def verify_otp(msisdn, otp):
    url = 'https://apim.djezzy.dz/oauth2/token'
    payload = f'otp={otp}&mobileNumber={msisdn}&scope=openid&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&client_secret=MVpXHW_ImuMsxKIwrJpoVVMHjRsa&grant_type=mobile'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    try:
        response = requests.post(url, data=payload, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# تطبيق الهدية
def apply_gift(chat_id, msisdn, access_token, username, name):
    user_data = load_user_data()

    url = f'https://apim.djezzy.dz/djezzy-api/api/v1/subscribers/{msisdn}/subscription-product?include='
    payload = {
        "data": {
            "id": "TransferInternet2Go",
            "type": "products",
            "meta": {
                "services": {
                    "steps": 10000,
                    "code": "FAMILY4000",
                    "id": "WALKWIN"
                }
            }
        }
    }
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response_data = response.json()
        if "successfully done" in response_data.get('message', ''):
            hidden_phone = hide_phone_number(msisdn)
            success_message = (
                f"✅ مبروك عليك الانترنت خو!\n\n"
                f"👤 الاسم: {name}\n"
                f"🧑‍💻 تيليجرام: @{username}\n"
                f"☎️ رقمك: {hidden_phone}\n"
            )
            bot.send_message(chat_id, success_message)
            user_data[str(chat_id)] = user_data.get(str(chat_id), {})
            user_data[str(chat_id)]['last_applied'] = datetime.now().isoformat()
            save_user_data(user_data)
            return True
        else:
            bot.send_message(chat_id, f"⚠️ خطأ: {response_data.get('message', 'مافهمناش وين المشكل')}")
            return False
    except:
        bot.send_message(chat_id, "⚠️ صار مشكل كي كنا نفعلولك، حاول تعاود.")
        return False

# أوامر البداية
@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

# رسالة ترحيب فيها الحقوق
    welcome = (
        "👋 مرحبا بيك ف بوت تفعيل هدية جيزي!\n\n"
        "👑 حقوق المطور: MAZIGH \n""📲 اضغط تحت باش تبعت رقمك."
    )
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='📱 إرسال رقم الهاتف', callback_data='send_number'))
    bot.send_message(chat_id, welcome, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'send_number')
def handle_send_number(callback_query):
    chat_id = callback_query.message.chat.id
    bot.send_message(chat_id, '📞 صبري معانا، بعتلنا رقمك دزايري يبدأ بـ 07:')
    bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_number)

def handle_phone_number(msg):
    chat_id = msg.chat.id
    text = msg.text
    if text.startswith('07') and len(text) == 10:
        msisdn = '213' + text[1:]
        if send_otp(msisdn):
            bot.send_message(chat_id, '✅ بعثنالكم الكود، فوتوهولنا هنا:')
            bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_otp(msg, msisdn))
        else:
            bot.send_message(chat_id, '⚠️ ماقدرناش نبعتولك الكود، جرب ثاني!')
    else:
        bot.send_message(chat_id, '⚠️ الرقم اللي بعثتو مش صحيح، جرب ثاني مع رقم يبدا بـ 07.')

def handle_otp(msg, msisdn):
    chat_id = msg.chat.id
    otp = msg.text
    tokens = verify_otp(msisdn, otp)
    if tokens:
        user_data = load_user_data()
        user_data[str(chat_id)] = {
            'username': msg.from_user.username,
            'telegram_id': chat_id,
            'msisdn': msisdn,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'last_applied': None
        }
        save_user_data(user_data)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='🎁 تفعيل الهدية', callback_data='walkwingift'))
        bot.send_message(chat_id, '✅ هايل! تحققنا منك بنجاح! دير اختيارك لتفعيل الهدية:', reply_markup=markup)
    else:
        bot.send_message(chat_id, '⚠️ الكود خطأ ولا راح مدة الصلاحية، جرب ثاني.')

@bot.callback_query_handler(func=lambda call: call.data == 'walkwingift')
def handle_walkwingift(callback_query):
    chat_id = callback_query.message.chat.id
    user_data = load_user_data()
    if str(chat_id) in user_data:
        user = user_data[str(chat_id)]
        apply_gift(chat_id, user['msisdn'], user['access_token'], user['username'], callback_query.from_user.first_name)

# حقوق المطور في الكونسول
print("👑 حقوق المطور: MAZIGH")
print("⚖️ إخلاء المسؤولية: لا يحق تعديل السكربت بلا إذن")
print('✅ البوت راهو يخدم بنجاح...')

bot.polling()
