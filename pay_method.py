# https://www.liqpay.ua/doc/api/internet_acquiring/card_payment?tab=1

from liqpay.liqpay3 import LiqPay
import time

public_key = ''
private_key = ''

liqpay = LiqPay(public_key, private_key)
def payment_details(amount:int, description:str, card:int, card_exp_month:int, card_exp_year:int, card_cvv:int):
    order_id = str(int(time.time()))
    res = liqpay.api("request", {
        "action"         : "pay",
        "version"        : "3",
        # "phone"          : "380901589224",
        "amount"         : amount,
        "currency"       : "UAH",
        "description"    : description,
        "order_id"       : order_id,
        "card"           : card,
        "card_exp_month" : card_exp_month,
        "card_exp_year"  : card_exp_year,
        "card_cvv"       : card_cvv
        })

    if res.get("status") == "success":
        return "Платіж успішний"
    elif res.get("status") == "failure":
        return "Помилка платежу"
    elif res.get("status") == "processing":
        return "Платіж обробляється"