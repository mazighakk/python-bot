import telebot
import requests
import json
import os
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = '8149056899:AAGBwImu7nAqGsPZyNt7wqUlhcQUomDa95s'
bot = telebot.TeleBot(TOKEN)
data_file_path = 'djezzy_data.json'

GIFT_INFO = {
    '1gb': {
        'product_id': 'TransferInternet1Go',
        'code': 'FAMILY1000',
        'display': '1GB'
    },
    '2gb': {
        'product_id': 'TransferInternet2Go',
        'code': 'FAMILY4000',
        'display': '2GB'
    },
    '500mb': {
        'product_id': 'TransferInternet500MB',
        'code': 'FAMILY500',
        'display': '500MB'
    }
}

def load_user_data():
    if os.path.exists(data_file_path):
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            os.remove(data_file_path)
            return {}
    return {}

def save_user_data(data):
    with open(data_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def hide_phone_number(phone):
    return phone[:4] + '***' + phone[-2:]

def send_otp(msisdn):
    url = 'https://apim.djezzy.dz/oauth2/registration'
    payload = f'msisdn={msisdn}&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&scope=smsotp'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post(url, data=payload, headers=headers, verify=False)
        return res.status_code == 200 or "confirmation code" in res.text.lower()
    except:
        return False

def verify_otp(msisdn, otp):
    url = 'https://apim.djezzy.dz/oauth2/token'
    payload = f'otp={otp}&mobileNumber={msisdn}&scope=openid&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&client_secret=MVpXHW_ImuMsxKIwrJpoVVMHjRsa&grant_type=mobile'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post(url, data=payload, headers=headers, verify=False)
        return res.json() if res.status_code == 200 else None
    except:
        return None

def apply_gift(chat_id, msisdn, token, username, name, gift_type):
    user_data = load_user_data()
    
    if gift_type not in GIFT_INFO:
        bot.send_message(chat_id, "⚠️ نوع الهدية غير صالح.")
        return
    
    gift_config = GIFT_INFO[gift_type]
    product_id = gift_config['product_id']
    code = gift_config['code']
    display_name = gift_config['display']
    
    url = f'https://apim.djezzy.dz/djezzy-api/api/v1/subscribers/{msisdn}/subscription-product?include='
    payload = {
        "data": {
            "id": product_id,
            "type": "products",
            "meta": {
                "services": {
                    "steps": 10000,
                    "code": code,
                    "id": "WALKWIN"
                }
            }
        }
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'Djezzy/2.6.7'
    }
    try:
        r = requests.post(url, json=payload, headers=headers, verify=False)
        data = r.json()
        if "successfully done" in str(data.get("message", "")):
            msg = (f"✅ تم منحك {display_name} بنجاح!\n"
                   f"👤 الاسم: {name}\n"
                   f"📞 الرقم: {hide_phone_number(msisdn[3:])}")
            bot.send_message(chat_id, msg)
        else:
            error_msg = data.get('message', 'خطأ غير معروف')
            bot.send_message(chat_id, f"⚠️ فشل الإرسال: {error_msg}")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ حدث خطأ أثناء الإرسال: {str(e)}")

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("▶️ إرسال الرقم", callback_data='send_number'))
    welcome_text = (
        "مرحباً بك في بوت هدايا Djezzy!\n\n"
        "للحصول على الهدية، أرسل رقمك الهاتف (يبدأ بـ 07):"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'send_number')
    def get_num(call):
        bot.send_message(call.message.chat.id, "📱 أرسل رقمك (يبدأ بـ 07):")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, handle_phone)
    
    def handle_phone(msg):
        chat_id = msg.chat.id
        text = msg.text.strip()
        if not (text.startswith("07") and len(text) == 10 and text.isdigit()):
            bot.send_message(chat_id, "❌ رقم غير صحيح.")
            return
        
        msisdn = '213' + text[1:]
        data = load_user_data()
        
        if str(chat_id) in data and data[str(chat_id)]['msisdn'] == msisdn:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(
                telebot.types.InlineKeyboardButton("1GB 🎁", callback_data='gift_1gb'),
                telebot.types.InlineKeyboardButton("2GB 🎁", callback_data='gift_2gb')
            )
            markup.row(telebot.types.InlineKeyboardButton("500MB 🎁", callback_data='gift_500mb'))
            bot.send_message(chat_id, "✅ مرحباً بك مجدداً! اختر الحجم المطلوب:", reply_markup=markup)
        else:
            if send_otp(msisdn):
                bot.send_message(chat_id, "✅ أرسل الرمز الذي وصلك:")
                bot.register_next_step_handler_by_chat_id(chat_id, lambda m: handle_otp(m, msisdn))
            else:
                bot.send_message(chat_id, "⚠️ فشل في إرسال الرمز.")
    
    def handle_otp(msg, msisdn):
        chat_id = msg.chat.id
        otp = msg.text.strip()
        if len(otp) != 6 or not otp.isdigit():
            bot.send_message(chat_id, "❌ رمز غير صالح.")
            return
        
        tokens = verify_otp(msisdn, otp)
        if tokens:
            data = load_user_data()
            data[str(chat_id)] = {
                'msisdn': msisdn,
                'username': msg.from_user.username or 'غير معروف',
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token']
            }
            save_user_data(data)
            
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(
                telebot.types.InlineKeyboardButton("1GB 🎁", callback_data='gift_1gb'),
                telebot.types.InlineKeyboardButton("2GB 🎁", callback_data='gift_2gb')
            )
            markup.row(telebot.types.InlineKeyboardButton("500MB 🎁", callback_data='gift_500mb'))
            bot.send_message(chat_id, "✅ تم التحقق بنجاح! اختر الحجم المطلوب:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ رمز خاطئ أو انتهت صلاحيته.")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('gift_'))
    def handle_gift_selection(call):
        chat_id = call.message.chat.id
        data = load_user_data()
        if str(chat_id) not in data:
            bot.send_message(chat_id, "❌ بياناتك غير موجودة. ابدأ من جديد باستخدام /start")
            return
        
        gift_type = call.data.split('_')[1]
        if gift_type not in GIFT_INFO:
            bot.answer_callback_query(call.id, "❌ خيار غير متاح")
            return
        
        user_info = data[str(chat_id)]
        apply_gift(
            chat_id=chat_id,
            msisdn=user_info['msisdn'],
            token=user_info['access_token'],
            username=user_info['username'],
            name=call.from_user.first_name or "مستخدم",
            gift_type=gift_type
        )
    
    print("🤖 البوت يعمل...")
    bot.polling()
