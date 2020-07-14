import telepot
import stripe
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

cdata = {}

TOKEN = '1073212465:AAEPgR1koz3100ls6rExEjO_NnfwWSBVoRI'
testkey = str(open('token.txt').read()).replace('\n', '').replace(' ', '')
stripe.api_key = testkey


def payment(amount, name, cardnum, cardmonth, cardyear, cardcvc, email, phone, description, country, city, address_line1, address_line2, zip):
    try:
        if cardnum not in cdata:
            token = stripe.Token.create(
                card={
                    "number": cardnum,
                    "exp_month": cardmonth,
                    "exp_year": cardyear,
                    "cvc": cardcvc,
                    "name":name,
                    "address_city":city,
                    "address_country":country,
                    "address_line1":address_line1,
                    "address_line2":address_line2,
                    "address_zip":zip
                },
            )
            # print(token)
            time.sleep(2)
            customer = stripe.Customer.create(
                card=token,
                email=email,
                phone=phone,
                description=description,
                name=name,
                address={'city':city, 'line1':address_line1, 'country':country}

            )
            # print(customer)
            cdata[cardnum] = customer.id
            customer_id = customer.id
        else:
            customer_id = cdata[cardnum]
    except stripe.error.CardError as e:
        print(e)
        return 'Invalid card'
    except stripe.error.RateLimitError as e:
        print(e)
        return 'Too many requests made'
    except stripe.error.InvalidRequestError as e:
        print(e)
        return 'Invalid card data'
    except stripe.error.AuthenticationError as e:
        print(e)
        return 'Connection failed. Try again'
    except stripe.error.APIConnectionError as e:
        print(e)
        return 'Connection failed. Try again'
    except stripe.error.StripeError as e:
        print(e)
        return 'Something went wrong. Try again.'
    except Exception as e:
        print(e)
        return 'Something went wrong. Try again.'

    charge = stripe.Charge.create(
        customer=customer_id,
        amount=int(float(amount) * 100),
        currency="usd",
        description=description,
        receipt_email=email,
        # shipping={
        # "address": {
        #     "city": city,
        #     "country": country,
        #     "line1": address_line1,
        #     "line2": address_line2,
        #     "postal_code": zip
        # },
        # 'name':name,
        # 'phone':phone
        # }
    )
    return charge.status

def handler(data):
    uid = data['from']['id']
    # print(data)
    if data['text'] == '/start':
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Pay')],
            ], resize_keyboard=True, one_time_keyboard=True)
            bot.sendMessage(uid, 'If you want to pay click pay', reply_markup=keyboard)
    elif data['text'].lower() == 'pay':
        bot.sendMessage(uid, 'Введите данные карты через |:\nAmount\nName\nCard number\nMonth\nYear\nCVC\nEmail\nPhone\nDescription\nCountry\nCity\nAddress line 1\nAddress line 2\nZip')
    else:
        paydata = data['text'].split('|')
        # print(paydata)
        for i in range(len(paydata)):
            if '-' in paydata[i]:
                paydata[i] = None

        try:
            bot.sendMessage(uid, payment(paydata[0],
                                         paydata[1],
                                         paydata[2],
                                         paydata[3],
                                         paydata[4],
                                         paydata[5],
                                         paydata[6],
                                         paydata[7],
                                         paydata[8],
                                         paydata[9],
                                         paydata[10],
                                         paydata[11],
                                         paydata[12],
                                         paydata[13]
                                         ))
        except Exception as e:
            print(e)
            bot.sendMessage(uid, 'Wrong data. Try again.')

bot = telepot.Bot(TOKEN)
# bot.deleteWebhook()
MessageLoop(bot, handler).run_as_thread()
print(bot.getMe())



while 1:
    time.sleep(1)