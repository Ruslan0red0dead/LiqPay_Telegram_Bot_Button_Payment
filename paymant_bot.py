from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from pay_method import payment_details
from config import TOKEN
import asyncio
import logging
import sys

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

router = Router()
dp.include_router(router)

# Створюємо стейти для кожного етапу введення реквізитів картки
class CardForm(StatesGroup):
    card_number = State()
    expiry_date = State()
    cvv = State()
    frozen = State()

keyboard_builder = ReplyKeyboardBuilder()

# Add the button to the builder
keyboard_builder.add(KeyboardButton(text="Оплатити"))
keyboard_builder.add(KeyboardButton(text="Змінити"))

# Build the keyboard with resize and input settings
keyboard = keyboard_builder.as_markup(resize_keyboard=True)

@dp.message(F.text.in_(['Змінити', 'Реквізити']))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer('Введіть номер картки:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(CardForm.card_number)

# Обробник введення номера картки
@dp.message(CardForm.card_number)
async def process_card_number(message: Message, state: FSMContext):
    card_number = message.text
    await state.update_data(card_number=card_number)
    
    await message.answer("Введіть термін дії картки (MM/YY):")
    await state.set_state(CardForm.expiry_date)

# Обробник введення терміну дії картки
@dp.message(CardForm.expiry_date)
async def process_expiry_date(message: Message, state: FSMContext):
    expiry_date = message.text
    await state.update_data(expiry_date=expiry_date)
    
    await message.answer("Введіть CVV код:")
    await state.set_state(CardForm.cvv)

# Обробник введення CVV
@dp.message(CardForm.cvv)
async def process_cvv(message: Message, state: FSMContext):
    cvv = message.text
    await state.update_data(cvv=cvv)

    # Отримуємо всі дані
    user_data = await state.get_data()
    
    card_number = user_data['card_number']

    expiry_date = user_data['expiry_date']

    cvv = user_data['cvv']
    """
    Згідно з політикою LiqPay, використання логотипу LiqPay під час оплати є обов'язковим.
    Це необхідно для забезпечення прозорості та впізнаваності бренду.
    Логотип повинен бути видимим на сторінці оплати або в інтерфейсі вашого додатка, щоб користувачі могли ідентифікувати, що вони користуються послугами LiqPay.
    """

    url = "https://logowik.com/content/uploads/images/liqpay8109.logowik.com.webp"

    await message.answer_photo(photo=url,caption=f"Твої реквізити:\nНомер картки: {card_number}\nТермін дії: {expiry_date}\nCVV: {cvv}",reply_markup=keyboard)

    await state.set_state(CardForm.frozen)

@dp.message(CardForm.frozen)
async def handle_payment_button(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    card_number = user_data['card_number']
    
    expiry_date = user_data['expiry_date']
    
    cvv = user_data['cvv']

    cleaned_date = expiry_date.replace("/", " ").strip()  # Заміна / на пробіл і видалення зайвих пробілів
    first_part, second_part = cleaned_date.split()

    if message.text == "Оплатити":
    	payment_result = payment_details(1,'Опис продукту',card_number,first_part,second_part,cvv)
    	if payment_result == 'Платіж успішний':
    		await message.answer(payment_result,reply_markup=ReplyKeyboardRemove())
    	elif payment_result == 'Помилка платежу':
    		await message.answer(payment_result)
    
    await state.clear()

async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())