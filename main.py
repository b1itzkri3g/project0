import asyncio
import logging
import sys
from os import getenv
from aiogram import F
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton,BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder,ReplyKeyboardBuilder
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database import DatabaseManager
from loader import db,dp,bot
import smile_one
import smile_one_ph
from datetime import datetime,timedelta
import json
import re
from aiogram.types import FSInputFile
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fpdf import FPDF
import unicodedata
from aiogram.types import InputFile
import io
from tempfile import gettempdir
import os
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import pytz
from zoneinfo import ZoneInfo
import html
from uuid import uuid4
from datetime import datetime
import asyncio
import re
import json
from zoneinfo import ZoneInfo

# Function to sanitize text to latin-1 compatible
def sanitize_to_latin1(text):
    return ''.join(
        char if char in ''.join(chr(i) for i in range(256)) else '?' for char in text
    )

class PDF(FPDF):
    def header(self):
        # Add logo
        self.image("lhp_logo.jpg", 10, 8, 33)  # Adjust the file path and dimensions as needed
        self.set_font("Arial", style="B", size=14)
        self.cell(0, 10, "Panda Recharge Bot - Diamond Price List", align="C", ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_table(self, headers, data, col_widths):
        self.set_font("Arial", size=10)

        # Table header
        self.set_fill_color(100, 149, 237)  # Cornflower blue
        self.set_text_color(255)  # White text for the header
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
        self.ln()

        # Table rows
        self.set_text_color(0)  # Reset text color
        self.set_fill_color(240, 240, 240)  # Light gray for alternating rows
        for idx, row in enumerate(data):
            fill = idx % 2 == 0  # Alternate row fill
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 10, str(cell), border=1, align="C", fill=fill)
            self.ln()

@dp.message(F.text==".noti")
async def send_welcome(message: types.Message):
    uid = db.fetchall('SELECT * FROM users')
    for u in uid:
        u_id = int(u[0])
        await bot.send_message(u_id,"hello")
    

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()

    builder.button(text=f"Login", callback_data=f"login")
    builder.button(text=f"Getid", callback_data=f"getid")
    builder.button(text=f"Help", callback_data=f"help")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!",reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == 'getid')
async def process_getid_click(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.answer(f"Your user ID is: {user_id}")


@dp.callback_query(lambda c: c.data == 'help')
async def process_getid_click(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.answer(f"Contact to an Admin\n")


class Form(StatesGroup):
    username = State()
    password = State()
    session = State()

credential = []


@dp.callback_query(lambda c: c.data == 'login')
async def process_login_click(callback_query: types.CallbackQuery,state: FSMContext)-> None:
    user_id = callback_query.from_user.id
    udx = db.fetchone('SELECT * FROM users WHERE user_id=?', (user_id,))
    if udx is not None:
        await state.set_state(Form.username)
        await callback_query.message.answer("Please enter your username: ")
    else:
        await callback_query.message.answer(f"You are not register. use /start to see menu")

@dp.message(Form.username)
async def get_username(message: types.Message,state: FSMContext)-> None:
    global credential
    user_id = message.from_user.id
    username = message.text
    credential.append(username)
    await state.set_state(Form.password)
    await message.answer("Please enter your password:")


@dp.message(Form.password)
async def get_username(message: types.Message,state: FSMContext)-> None:

    global credential
    user_id = message.from_user.id
    password = message.text
    credential.append(password)
    username_db = db.fetchone('SELECT username FROM users WHERE user_id=?', (user_id,))
    password_db = db.fetchone('SELECT password FROM users WHERE user_id=?', (user_id,))
    username_db = ''.join(username_db)
    password_db = ''.join(password_db)
    if credential[0] == username_db and credential[1] == password_db:
        credential = []
        await show_menu(message) 
        await state.set_state(Form.session)
    else:
        credential = []
        await message.answer('Login failed')
        await state.clear()

# Define a custom CallbackData subclass
class PaginationCallback(CallbackData, prefix="pagination"):
    page: int

@dp.callback_query(F.data == "view_history")
async def history(query: types.CallbackQuery, state: FSMContext) -> None:
    main_user = query.from_user.id
    my_tran = db.fetchall('SELECT * FROM transcation WHERE main_user=?', (main_user,))

    if my_tran:
        await send_paginated_history(query.message, my_tran, page=1)
    else:
        await query.message.answer("You have no transaction history.")
    await query.answer()  # Acknowledge the callback query

async def send_paginated_history(message: types.Message, transactions: list, page: int) -> None:
    per_page = 10  # Number of transactions per page
    total_pages = -(-len(transactions) // per_page)  # Ceiling division to calculate total pages

    # Get transactions for the current page
    start = (page - 1) * per_page
    end = start + per_page
    transactions_page = transactions[start:end]

    # Build the message
    history_message = f"Transaction History (Page {page}/{total_pages}):\n\n"
    for tran in transactions_page:
        history_message += f"Transaction ID: {tran[0]}\n"
        history_message += f"Details: {tran[1]}\n"
        history_message += f"Amount: {tran[2]}\n"
        history_message += f"Date: {tran[3]}\n"
        history_message += f"Status: {tran[4]}\n"
        history_message += "--------------------------------\n"

    # Add navigation buttons
    buttons = []
    if page > 1:
        buttons.append(types.InlineKeyboardButton(
            text="⬅️ Previous", 
            callback_data=PaginationCallback(page=page - 1).pack()
        ))
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton(
            text="Next ➡️", 
            callback_data=PaginationCallback(page=page + 1).pack()
        ))

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer(history_message, reply_markup=keyboard)

@dp.callback_query(PaginationCallback.filter())
async def pagination_callback(query: types.CallbackQuery, callback_data: PaginationCallback) -> None:
    page = callback_data.page
    main_user = query.from_user.id
    my_tran = db.fetchall('SELECT * FROM transcation WHERE main_user=?', (main_user,))

    # Edit the message with the requested page
    await query.message.edit_text(text="Loading...", reply_markup=None)
    await send_paginated_history(query.message, my_tran, page=page)
    await query.answer()



@dp.callback_query(F.data == "price_list")
async def pricelist(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    # Fetch data from the database
    pri = db.fetchall('SELECT * FROM dia_price')
    pri_ph = db.fetchall('SELECT * FROM dia_price_ph')

    # Prepare data for tables
    headers = ["#", "Diamonds", "Coins"]
    region1_data = [[idx + 1, item[1], item[2]] for idx, item in enumerate(pri)]
    region2_data = [[idx + 1, item[1], item[2]] for idx, item in enumerate(pri_ph)]

    # Generate a price list PDF
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add Region 1 Table
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Diamond Price List (Brazil Region)", ln=True)
    pdf.ln(5)
    pdf.add_table(headers, region1_data, [10, 80, 50])

    pdf.ln(10)

    # Add Region 2 Table
    pdf.cell(0, 10, "Diamond Price List (Philippines Region)", ln=True)
    pdf.ln(5)
    pdf.add_table(headers, region2_data, [10, 80, 50])

    # Save the PDF to a file
    pdf_file_path = "price_list.pdf"
    pdf.output(pdf_file_path)

    # Send the PDF file
    await callback_query.message.answer_document(FSInputFile(pdf_file_path))

    # Inline menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷 Check smileone.com Pricelist", url="https://www.smile.one/")],
        [InlineKeyboardButton(text="🏠 Back to Menu", callback_data="back_to_menu")],
    ])
    await callback_query.message.answer(
        "🎉 Explore the website for more options or return to the main menu:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback_query: types.CallbackQuery) -> None:
    # Handle redirection to the menu
    await callback_query.message.answer("📋 Returning to the main menu...")

    # Access the bot instance directly from the bot object
    await show_menu(callback_query.message)  # Pass the message to show_menu

    await callback_query.answer()  # Acknowledge the callback







async def send_beautified_voucher(message, tran_id, diamond, actual_wp, userid, zoneid, username, status, coin_value, my_bal, formatted_date_str):
    # Escape user-generated inputs to prevent HTML parsing errors
    safe_tran_id = html.escape(tran_id)
    safe_userid = html.escape(userid)
    safe_zoneid = html.escape(zoneid)
    safe_username = html.escape(username)
    safe_status = html.escape(status)
    safe_formatted_date_str = html.escape(formatted_date_str)

    if actual_wp == 0:
        # Diamond Voucher
        beautified_text = (
            f"🎟️ Payment Voucher\n"
            f"====================\n"
            f"📜 Transaction ID: {safe_tran_id}\n\n"
            f"Product: {diamond} Diamonds\n"
            f"User ID: {safe_userid} ({safe_zoneid})\n"
            f"Username: {safe_username}\n"
            f"Status: ✅{safe_status}\n\n"
            f"💰 Debited from Balance: ${coin_value}\n"
            f"📉 Remaining Balance: ${my_bal}\n"
            f"🗓️ Date: {safe_formatted_date_str}"
        )
    else:
        # WP Voucher
        beautified_text = (
            f"🎟️ Payment Voucher\n"
            f"====================\n"
            f"📜 Transaction ID: {safe_tran_id}\n\n"
            f"Product: {actual_wp} wp\n"
            f"User ID: {safe_userid} ({safe_zoneid})\n"
            f"Username: {safe_username}\n"
            f"Status: ✅{safe_status}\n\n"
            f"💰 Debited from Balance: ${coin_value}\n"
            f"📉 Remaining Balance: ${my_bal}\n"
            f"🗓️ Date: {safe_formatted_date_str}"
        )
    
    # Send with HTML parse mode, ensuring escaped characters are handled correctly
    await message.answer(beautified_text, parse_mode='HTML')



def remove_unsupported_characters(text):
    """Remove unsupported characters for FPDF (supports only Latin-1)."""
    return re.sub(r'[^\x20-\x7E]', '', text)

def generate_pdf_voucher(tran_id, diamond, actual_wp, userid, zoneid, username, status, coin_value, my_bal, formatted_date):
    # Use a temporary directory to save the file
    temp_dir = gettempdir()
    file_path = os.path.join(temp_dir, f"Payment_Voucher_{tran_id}.pdf")

    # Initialize the PDF object
    pdf = FPDF(format='A4')
    pdf.add_page()

    # Add a logo
    logo_path = "lhp_logo.jpg"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
        pdf.ln(20)

    # Set title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Payment Voucher", ln=True, align="C")
    pdf.ln(10)

    # Voucher details
    pdf.set_font("Helvetica", size=12)
    fields = [
        ("Transaction ID", tran_id),
        ("Product", f"{diamond} Diamonds"),
        ("Successful WP", actual_wp),
        ("User ID", userid),
        ("Zone ID", zoneid),
        ("Username", username),
        ("Status", status),
        ("Debited from Balance", f"${coin_value:.2f}"),
        ("Remaining Balance", f"${my_bal:.2f}"),
        ("Date", formatted_date)
    ]

    # Add details to PDF, removing unsupported characters
    for field, value in fields:
        clean_field = remove_unsupported_characters(field)
        clean_value = remove_unsupported_characters(str(value))
        pdf.cell(50, 10, clean_field, border=1)
        pdf.cell(80, 10, clean_value, border=1)
        pdf.ln()

    # Save the PDF
    pdf.output(file_path)
    return file_path
async def process_toupup_voucher(message, tran_id, diamond, actual_wp, userid, zoneid, username, status, coin_value, my_bal, formatted_date):

    # Generate PDF voucher
    file_path = generate_pdf_voucher(
        tran_id=tran_id,
        diamond=diamond,
        actual_wp=actual_wp,
        userid=userid,
        zoneid=zoneid,
        username=username,
        status=status,
        coin_value=coin_value,
        my_bal=my_bal,
        formatted_date=formatted_date
    )



    # Send beautified voucher text
    await send_beautified_voucher(message, tran_id, diamond, actual_wp, userid, zoneid, username, status, coin_value, my_bal, formatted_date)

    #pdf_file = FSInputFile(file_path)
    #await message.answer_document(pdf_file, caption="🎟️ Here is your payment voucher as a PDF.")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Separate storage for .b command
pending_confirmations_b = {}
user_locks_b = {}

@dp.message(F.text.regexp(r'\.b'))
async def toupup_b(message: types.Message) -> None:
    user_id = message.from_user.id
    confirm_config = db.fetchone("SELECT confirm_button FROM users WHERE user_id=?", (user_id,))
    confirm_required = confirm_config and str(confirm_config[0]).lower() == "yes"
    
    try:
        accounts_text = message.text.split('.b', 1)[1].strip()
    except IndexError:
        await message.answer(
            "❌ Invalid command format. Use:\n"
            "Format A: .b userid(zoneid)diamond,userid2(zone2)diamond2,...\n"
            "Format B: .b userid zoneid diamond,userid2 zone2 diamond2,..."
        )
        return

    if confirm_required:
        confirmation_id = str(uuid4())
        pending_confirmations_b[confirmation_id] = {
            "user_id": user_id,
            "accounts_text": accounts_text,
            "timestamp": datetime.now().timestamp()
        }
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅Confirm", callback_data=f"confirm_topup_b:{confirmation_id}"),
             InlineKeyboardButton(text="🛑Cancel", callback_data=f"cancel_topup_b:{confirmation_id}")]
        ])
        await message.answer("Please confirm your topup.", reply_markup=markup)
    else:
        lock = user_locks_b.setdefault(user_id, asyncio.Lock())
        async with lock:
            await process_topup_b(accounts_text, user_id, message)

@dp.callback_query(lambda c: c.data.startswith("confirm_topup_b:"))
async def confirm_topup_b(callback: types.CallbackQuery) -> None:
    confirmation_id = callback.data.split(":", 1)[1]
    data = pending_confirmations_b.get(confirmation_id)
    
    if not data or data["user_id"] != callback.from_user.id:
        await callback.answer("Invalid or expired confirmation!", show_alert=True)
        return
    
    del pending_confirmations_b[confirmation_id]
    await callback.answer()
    await callback.message.edit_text("⏳ Processing your topup...")
    
    user_id = callback.from_user.id
    lock = user_locks_b.setdefault(user_id, asyncio.Lock())
    async with lock:
        await process_topup_b(data["accounts_text"], user_id, callback.message)

@dp.callback_query(lambda c: c.data.startswith("cancel_topup_b:"))
async def cancel_topup_b(callback: types.CallbackQuery) -> None:
    confirmation_id = callback.data.split(":", 1)[1]
    if confirmation_id in pending_confirmations_b:
        if pending_confirmations_b[confirmation_id]["user_id"] == callback.from_user.id:
            del pending_confirmations_b[confirmation_id]
    await callback.answer("Topup canceled!", show_alert=True)
    await callback.message.edit_text("❌ Topup has been canceled")

async def process_topup_b(accounts_text: str, user_id: int, message: types.Message) -> None:
    main_user = user_id
    price_l = {
        '13': 61.50, '23': 122.00, '25': 177.50, '26': 480.00,
        '27': 1453.00, '28': 2424.00, '29': 3660.00, '30': 6079.00,
        '20340': 229.71, '33': 402.5, '22590': 39, '22591': 116.9,
        '22592': 187.5, '22593': 385, '22594': 39
    }
    id_list = [
        '13', '23', '25', '25+23', '25+25', '25+25+13', '26', '26+23',
        '26+26', '27', '28', '29', '30', '', '', '', '', '', '',
        '', '', '', '', '25+13', '26+25+13', '26+13', '27+26', '26+25',
        '26+25+23', '20340', '33', '22590', '22591', '22592', '22593', '22594','26+26+28','26+25+25'
    ]
    
    async def process_single_account(account_str: str):
        try:
            if "(" in account_str and ")" in account_str:
                clean_str = re.sub(r"[\t\s]*", "", account_str)
                userid, rest = clean_str.split("(", 1)
                zoneid, diamond = rest.split(")", 1)
            else:
                parts = account_str.split()
                if len(parts) != 3:
                    raise ValueError("Expected three parts (userid, zoneid, diamond)")
                userid, zoneid, diamond = parts

            my_bal_row = db.fetchone('SELECT amount FROM balance WHERE user_id=?', (user_id,))
            if not my_bal_row:
                await message.answer("❌ Could not retrieve your balance")
                return
            my_bal = float(my_bal_row[0])
            
            yangon_tz = ZoneInfo("Asia/Yangon")
            current_date = datetime.now(tz=yangon_tz).strftime("%Y %m %d")

            if "wp" in diamond:
                if diamond.startswith("wp"):
                    pack_number = diamond[len("wp"):]
                else:
                    pack_number = diamond.split("wp")[0]
                    
                pri = db.fetchall('SELECT package_no, diamond, price FROM dia_price')
                coin_value = next((price for pkg, d, price in pri if d == diamond), None)
                package_no = next((pkg for pkg, d, price in pri if d == diamond), None)
                
                account_info = await smile_one.get_role(userid, zoneid, '16642')
                data = json.loads(account_info)
                
                if data.get("status") == 201:
                    await message.answer(f"Ban Server")
                    return
                if data.get("message") != "success":
                    await message.answer(f"❌ Invalid account: {userid} {zoneid}")
                    return
                username = data['username']
                
                tran_id = []
                status = "success"
                if float(coin_value) > my_bal:
                    await message.answer("❌ Insufficient balance")
                    return
                
                for _ in range(int(pack_number)):
                    purchase = await smile_one.get_purchase(userid, zoneid, '16642')
                    try:
                        pur_data = json.loads(purchase)
                        if pur_data['message'] == 'success':
                            actual_wp += 1
                            tran_id.append(pur_data['order_id'])
                        else:
                            coin_value -= 76
                    except json.JSONDecodeError:
                        coin_value -= 76
                
                my_bal -= coin_value
                db.query("UPDATE balance SET amount=? WHERE user_id=?", (my_bal, user_id))
                db.query(
                    "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                    (user_id, diamond, coin_value, current_date, status, main_user)
                )
                
                await process_toupup_voucher(
                    message,
                    tran_id="\n".join(tran_id),
                    diamond=diamond,
                    actual_wp=actual_wp,
                    userid=userid,
                    zoneid=zoneid,
                    username=username,
                    status=status,
                    coin_value=coin_value,
                    my_bal=my_bal,
                    formatted_date=current_date
                )
            else:
                pri = db.fetchall('SELECT package_no, diamond, price FROM dia_price WHERE package_no NOT BETWEEN 14 AND 23')
                coin_value = next((price for pkg, d, price in pri if str(d) == str(diamond)), None)
                package_no = next((pkg for pkg, d, price in pri if str(d) == str(diamond)), None)
                
                if not package_no or package_no - 1 >= len(id_list):
                    await message.answer(f"⚠️ Invalid diamond package: {diamond}")
                    return
                product_id = id_list[package_no - 1]
                
                if '+' in product_id:
                    sub_products = product_id.split('+')
                    all_verified = True
                    username = None
                    for sp in sub_products:
                        account_info = await smile_one.get_role(userid, zoneid, sp)
                        data = json.loads(account_info)
                        if data.get("status") == 201:
                            await message.answer(f"Ban Server")
                            return
                        if data.get("message") != "success":
                            await message.answer(f"❌ Invalid account: {userid} {zoneid} for product {sp}")
                            all_verified = False
                            break
                        username = data['username']
                    if not all_verified:
                        return
                    
                    if coin_value > my_bal:
                        await message.answer("❌ Insufficient balance")
                        return
                    
                    tran_id = []
                    status = "success"
                    for sp in sub_products:
                        purchase = await smile_one.get_purchase(userid, zoneid, sp)
                        try:
                            pur_data = json.loads(purchase)
                            if pur_data["message"] != 'success':
                                status = "fail"
                                tran_id.append(f"Failed transaction for product {sp}")
                            else:
                                tran_id.append(pur_data['order_id'])
                        except json.JSONDecodeError:
                            status = "fail"
                            tran_id.append(f"Failed transaction for product {sp}")
                    
                    my_bal -= coin_value
                    db.query("UPDATE balance SET amount=? WHERE user_id=?", (my_bal, user_id))
                    db.query(
                        "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                        (user_id, diamond, coin_value, current_date, status, main_user)
                    )
                    
                    await process_toupup_voucher(
                        message,
                        tran_id="\n".join(tran_id),
                        diamond=diamond,
                        actual_wp=0,
                        userid=userid,
                        zoneid=zoneid,
                        username=username,
                        status=status,
                        coin_value=coin_value,
                        my_bal=my_bal,
                        formatted_date=current_date
                    )
                else:
                    account_info = await smile_one.get_role(userid, zoneid, product_id)
                    data = json.loads(account_info)
                    if data.get("status") == 201:
                        await message.answer(f"Ban Server")
                        return
                    if data.get("message") != "success":
                        await message.answer(f"❌ Invalid account: {userid} {zoneid}")
                        return
                    username = data['username']
                    
                    tran_id = []
                    status = "success"
                    if coin_value > my_bal:
                        await message.answer("❌ Insufficient balance")
                        return
                    
                    purchase = await smile_one.get_purchase(userid, zoneid, product_id)
                    try:
                        pur_data = json.loads(purchase)
                        if pur_data["message"] != 'success':
                            status = "fail"
                            coin_value -= price_l.get(str(product_id), 0)
                            tran_id.append("Failed transaction")
                        else:
                            tran_id.append(pur_data['order_id'])
                    except json.JSONDecodeError:
                        coin_value -= price_l.get(str(product_id), 0)
                        status = "fail"
                    
                    my_bal -= coin_value
                    db.query("UPDATE balance SET amount=? WHERE user_id=?", (my_bal, user_id))
                    db.query(
                        "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                        (user_id, diamond, coin_value, current_date, status, main_user)
                    )
                    
                    await process_toupup_voucher(
                        message,
                        tran_id="\n".join(tran_id),
                        diamond=diamond,
                        actual_wp=0,
                        userid=userid,
                        zoneid=zoneid,
                        username=username,
                        status=status,
                        coin_value=coin_value,
                        my_bal=my_bal,
                        formatted_date=current_date
                    )
        except Exception as e:
            await message.answer(f"⚠️ Error processing {account_str}: {str(e)}")
            logger.exception(f"Error processing {account_str}")

    accounts = accounts_text.split(',')
    for account in accounts:
        if account.strip():
            await process_single_account(account.strip())




pending_confirmations = {}
user_locks = {}

@dp.message(F.text.regexp(r'\.p'))
async def toupup(message: types.Message) -> None:  # Removed state parameter
    user_id = message.from_user.id

    # Get confirmation setting
    confirm_config = db.fetchone("SELECT confirm_button FROM users WHERE user_id=?", (user_id,))
    confirm_required = confirm_config and str(confirm_config[0]).lower() == "yes"

    try:
        accounts_text = message.text.split('.p', 1)[1].strip()
    except IndexError:
        await message.answer(
            "❌ Invalid command format. Use:\n"
            "Format A: .p userid(zoneid)diamond,userid2(zone2)diamond2,...\n"
            "Format B: .p userid zoneid diamond,userid2 zone2 diamond2,..."
        )
        return

    if confirm_required:
        # Generate unique confirmation ID
        confirmation_id = str(uuid4())
        pending_confirmations[confirmation_id] = {
            "user_id": user_id,
            "accounts_text": accounts_text,
            "timestamp": datetime.now().timestamp()
        }

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅Confirm", callback_data=f"confirm_topup_ph:{confirmation_id}"),
             InlineKeyboardButton(text="🛑Cancel", callback_data=f"cancel_topup_ph:{confirmation_id}")]
        ])
        await message.answer("Please confirm your topup.", reply_markup=markup)
    else:
        # Acquire per-user lock
        lock = user_locks.setdefault(user_id, asyncio.Lock())
        async with lock:
            await process_topup_ph(accounts_text, user_id, message)

@dp.callback_query(lambda c: c.data.startswith("confirm_topup_ph:"))
async def confirm_topup(callback: types.CallbackQuery) -> None:
    confirmation_id = callback.data.split(":", 1)[1]
    data = pending_confirmations.get(confirmation_id)
    
    if not data or data["user_id"] != callback.from_user.id:
        await callback.answer("Invalid or expired confirmation!", show_alert=True)
        return
    
    # Remove confirmation data
    del pending_confirmations[confirmation_id]
    await callback.answer()
    await callback.message.edit_text("⏳ Processing your topup...")
    
    # Acquire per-user lock
    user_id = callback.from_user.id
    lock = user_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        await process_topup_ph(data["accounts_text"], user_id, callback.message)

@dp.callback_query(lambda c: c.data.startswith("cancel_topup_ph:"))
async def cancel_topup(callback: types.CallbackQuery) -> None:
    confirmation_id = callback.data.split(":", 1)[1]
    if confirmation_id in pending_confirmations:
        if pending_confirmations[confirmation_id]["user_id"] == callback.from_user.id:
            del pending_confirmations[confirmation_id]
    
    await callback.answer("Topup canceled!", show_alert=True)
    await callback.message.edit_text("❌ Topup has been canceled")

async def process_topup_ph(accounts_text: str, user_id: int, message: types.Message) -> None:
    main_user = user_id
    price_l = {
        '212': 10.00, '213': 19.00, '214': 47.50, '215': 95.00,
        '216': 190.00, '217': 285.00, '218': 475.00, '219': 950.00,
        '20338': 229.71,'22600': 47.45,'22601':143.00,'22602':236,'22603':473,'22604':47.45
    }
    id_list = ['212','213','214','215','216','217','218','219','20338','22600','22601','22602','22603','','','','','','','','','','','22604']

    async def process_single_account(account_str: str):
        try:
            if "(" in account_str and ")" in account_str:
                clean_str = re.sub(r"[\n\t\s]*", "", account_str)
                userid, rest = clean_str.split("(", 1)
                zoneid, diamond = rest.split(")", 1)
            else:
                parts = account_str.split()
                if len(parts) != 3:
                    raise ValueError("Expected three parts (userid, zoneid, diamond)")
                userid, zoneid, diamond = parts

            try:
                my_bal_row = db.fetchone('SELECT amount FROM balance_ph WHERE user_id=?', (user_id,))
                if not my_bal_row:
                    await message.answer("❌ Could not retrieve your balance")
                    return

                my_bal = float(my_bal_row[0])
                yangon_tz = ZoneInfo("Asia/Yangon")
                current_date = datetime.now(tz=yangon_tz).strftime("%Y %m %d")

                # WP Package handling
                if "wp" in diamond:
                    pack_number = re.sub(r"\D", "", diamond)
                    actual_wp = 0

                    pri = db.fetchall('SELECT package_no, diamond, price FROM dia_price_ph')
                    coin_value = next((price for pkg, d, price in pri if d == diamond), None)
                    package_no = next((pkg for pkg, d, price in pri if d == diamond), None)

                    account_info = await smile_one_ph.get_role(userid, zoneid, '16641')
                    data = json.loads(account_info)
                    if data.get("status") == 201:
                        await message.answer(f"Ban Server")
                        return
                    if data.get("message") != "success":
                        await message.answer(f"❌ Invalid account: {userid} {zoneid}")
                        return

                    username = data['username']
                    tran_id = []
                    status = "success"

                    if float(coin_value) > my_bal:
                        await message.answer("❌ Insufficient balance")
                        return

                    for _ in range(int(pack_number)):
                        purchase = await smile_one_ph.get_purchase(userid, zoneid, '16641')
                        try:
                            pur_data = json.loads(purchase)
                            if pur_data['message'] == 'success':
                                actual_wp += 1
                                tran_id.append(pur_data['order_id'])
                            else:
                                coin_value -= 95
                        except json.JSONDecodeError:
                            coin_value -= 95

                    my_bal -= coin_value
                    db.query("UPDATE balance_ph SET amount=? WHERE user_id=?", (my_bal, user_id))
                    db.query(
                        "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                        (user_id, diamond, coin_value, current_date, status, main_user)
                    )

                    await process_toupup_voucher(
                        message,
                        tran_id="\n".join(tran_id),
                        diamond=diamond,
                        actual_wp=actual_wp,
                        userid=userid,
                        zoneid=zoneid,
                        username=username,
                        status=status,
                        coin_value=coin_value,
                        my_bal=my_bal,
                        formatted_date=current_date
                    )

                else:
                    pri = db.fetchall('SELECT package_no, diamond, price FROM dia_price_ph WHERE package_no NOT BETWEEN 14 AND 23')
                    coin_value = next((price for pkg, d, price in pri if str(d) == str(diamond)), None)
                    package_no = next((pkg for pkg, d, price in pri if str(d) == str(diamond)), None)
                    
                    if not package_no or package_no - 1 >= len(id_list):
                        await message.answer(f"⚠️ Invalid diamond package: {diamond}")
                        return

                    product_id = id_list[package_no - 1]
                    
                    if '+' in product_id:
                        sub_products = product_id.split('+')
                        all_verified = True
                        username = None
                        for sp in sub_products:
                            account_info = await smile_one_ph.get_role(userid, zoneid, sp)
                            data = json.loads(account_info)
                            if data.get("status") == 201:
                                await message.answer(f"Ban Server")
                                return
                            if data.get("message") != "success":
                                await message.answer(f"❌ Invalid account: {userid} {zoneid} for product {sp}")
                                all_verified = False
                                break
                            username = data['username']
                        if not all_verified:
                            return

                        if coin_value > my_bal:
                            await message.answer("❌ Insufficient balance")
                            return

                        tran_id = []
                        status = "success"
                        for sp in sub_products:
                            purchase = await smile_one_ph.get_purchase(userid, zoneid, sp)
                            try:
                                pur_data = json.loads(purchase)
                                if pur_data["message"] != 'success':
                                    status = "fail"
                                    tran_id.append(f"Failed transaction for product {sp}")
                                else:
                                    tran_id.append(pur_data['order_id'])
                            except json.JSONDecodeError:
                                status = "fail"
                                tran_id.append(f"Failed transaction for product {sp}")

                        my_bal -= coin_value
                        db.query("UPDATE balance_ph SET amount=? WHERE user_id=?", (my_bal, user_id))
                        db.query(
                            "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                            (user_id, diamond, coin_value, current_date, status, main_user)
                        )

                        await process_toupup_voucher(
                            message,
                            tran_id="\n".join(tran_id),
                            diamond=diamond,
                            actual_wp=0,
                            userid=userid,
                            zoneid=zoneid,
                            username=username,
                            status=status,
                            coin_value=coin_value,
                            my_bal=my_bal,
                            formatted_date=current_date
                        )

                    else:
                        account_info = await smile_one_ph.get_role(userid, zoneid, product_id)
                        data = json.loads(account_info)
                        if data.get("status") == 201:
                            await message.answer(f"Ban Server")
                            return
                        if data.get("message") != "success":
                            await message.answer(f"❌ Invalid account: {userid} {zoneid}")
                            return

                        username = data['username']
                        tran_id = []
                        status = "success"

                        if coin_value > my_bal:
                            await message.answer("❌ Insufficient balance")
                            return

                        purchase = await smile_one_ph.get_purchase(userid, zoneid, product_id)
                        try:
                            pur_data = json.loads(purchase)
                            if pur_data["message"] != 'success':
                                status = "fail"
                                coin_value -= price_l.get(str(product_id), 0)
                                tran_id.append("Failed transaction")
                            else:
                                tran_id.append(pur_data['order_id'])
                        except json.JSONDecodeError:
                            coin_value -= price_l.get(str(product_id), 0)
                            status = "fail"

                        my_bal -= coin_value
                        db.query("UPDATE balance_ph SET amount=? WHERE user_id=?", (my_bal, user_id))
                        db.query(
                            "INSERT INTO transcation VALUES (?,?,?,?,?,?)",
                            (user_id, diamond, coin_value, current_date, status, main_user)
                        )

                        await process_toupup_voucher(
                            message,
                            tran_id="\n".join(tran_id),
                            diamond=diamond,
                            actual_wp=0,
                            userid=userid,
                            zoneid=zoneid,
                            username=username,
                            status=status,
                            coin_value=coin_value,
                            my_bal=my_bal,
                            formatted_date=current_date
                        )

            except Exception as e:
                await message.answer(f"⚠️ Error processing {account_str}: {str(e)}")
                logger.exception(f"Error processing {account_str}")

        except Exception as e:
            await message.answer(f"⚠️ Invalid format: {account_str}")

    # Process all accounts
    accounts = accounts_text.split(',')
    for account in accounts:
        if account.strip():
            await process_single_account(account.strip())


@dp.callback_query(F.data == "check_balance")
async def check_balance(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    # Fetching balance from the database
    my_bal = db.fetchone('SELECT amount FROM balance WHERE user_id=?', (user_id,))
    my_bal_ph = db.fetchone('SELECT amount FROM balance_ph WHERE user_id=?', (user_id,))
    
    # Preparing responses
    balance_message = f"Your balance is: {hbold(my_bal[0])} Coins 😊"
    balance_ph_message = f"Your PH balance is: {hbold(my_bal_ph[0])} Coins 😊"
    
    # Sending responses
    await callback_query.message.answer(balance_message)
    await callback_query.message.answer(balance_ph_message)
    
    # Optionally acknowledge the callback query to avoid interaction issues
    await callback_query.answer()


    
# States for selecting date range
class DateRangeState(StatesGroup):
    awaiting_start_date = State()
    awaiting_end_date = State()


class DateSingleState(StatesGroup):
    awaiting_single_date = State()

# Helper function to fetch data
def fetch_transactions(user_id, start_date=None, end_date=None):
    query = "SELECT diamond FROM transcation WHERE user_id=? and status='success'"
    params = [user_id]
    def format_date(date_input):
        if hasattr(date_input, 'strftime'):
            return date_input.strftime("%Y %m %d")
        # Parse string input (e.g., "YYYY-MM-DD" to "YYYY MM DD")
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y %m %d")
        except ValueError:
            # Handle invalid formats
            raise ValueError("Date string must be in 'YYYY-MM-DD' format")

    if start_date and end_date:
        query += " AND t_date BETWEEN ? AND ?"
        params.extend([format_date(start_date), format_date(end_date)])
    elif start_date:
        print(start_date)
        query += " AND t_date=?"
        params.append(format_date(start_date))
        print(format_date(start_date))
    return db.fetchall(query, params)

def generate_voucher_pdf(transactions, title, filename):
    pdf = FPDF()
    pdf.add_page()
    
    # Add logo
    logo_path = "lhp_logo.jpg"
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=30)  # Adjust the x, y, and w as needed
        pdf.ln(20)  # Add some space after the logo
    
    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(10)

    # Add table header
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_fill_color(200, 220, 255)  # Light blue background for the header
    pdf.cell(50, 10, "Diamond", border=1, align="C", fill=True)
    pdf.cell(50, 10, "Count", border=1, align="C", fill=True)
    pdf.ln()

    # Counting diamonds
    number_count = {}
    for trans in transactions:
        diamond = trans[0]
        number_count[diamond] = number_count.get(diamond, 0) + 1

    # Table rows
    pdf.set_font("Arial", size=10)
    for diamond, count in number_count.items():
        pdf.cell(50, 10, txt=str(diamond), border=1, align="C")
        pdf.cell(50, 10, txt=str(count), border=1, align="C")
        pdf.ln()

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Generated by Panda Recharge Bot © 2025", align="C")

    # Save to file
    pdf.output(filename)

@dp.callback_query(F.data == "voucher")
async def voucher_options(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Today", callback_data="today")],
        [InlineKeyboardButton(text="Yesterday", callback_data="yesterday")],
        [InlineKeyboardButton(text="This Month", callback_data="this_month")],
        [InlineKeyboardButton(text="All Time", callback_data="all_time")],
        [InlineKeyboardButton(text="Select Date", callback_data="select_date")],
        [InlineKeyboardButton(text="Select Range", callback_data="select_range")],
    ])
    
    await callback_query.answer()  # Acknowledge the callback query
    await callback_query.message.answer(
        "Choose an option to view your vouchers:",
        reply_markup=keyboard
    )

# Callback handler for "Today"
@dp.callback_query(F.data == "today")
async def process_today(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")
    transactions = fetch_transactions(user_id, start_date=today)

    filename = f"voucher_today_{user_id}.pdf"
    generate_voucher_pdf(transactions, f"Voucher for {today}", filename)

    # Use FSInputFile to send the file
    file_input = FSInputFile(filename)
    await callback_query.message.answer_document(file_input)

# Callback handler for "Yesterday"
@dp.callback_query(F.data == "yesterday")
async def process_yesterday(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    transactions = fetch_transactions(user_id, start_date=yesterday)

    filename = f"voucher_yesterday_{user_id}.pdf"
    generate_voucher_pdf(transactions, f"Voucher for {yesterday}", filename)
    file_input = FSInputFile(filename)
    await callback_query.message.answer_document(file_input)

# Callback handler for "This Month"
@dp.callback_query(F.data == "this_month")
async def process_this_month(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    today = datetime.now()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    transactions = fetch_transactions(user_id, start_date=start_date, end_date=end_date)

    filename = f"voucher_this_month_{user_id}.pdf"
    generate_voucher_pdf(transactions, f"Voucher for {start_date} to {end_date}", filename)
    file_input = FSInputFile(filename)
    await callback_query.message.answer_document(file_input)

# Callback handler for "All Time"
@dp.callback_query(F.data == "all_time")
async def process_all_time(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    transactions = fetch_transactions(user_id)

    filename = f"voucher_all_time_{user_id}.pdf"
    generate_voucher_pdf(transactions, "Voucher for All Time", filename)
    file_input = FSInputFile(filename)
    await callback_query.message.answer_document(file_input)

# Callback handler for "Select Date"
@dp.callback_query(F.data == "select_date")
async def process_select_date(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Please type the date in the format `YYYY-MM-DD`:")
    await state.set_state(DateSingleState.awaiting_single_date)

@dp.message(DateSingleState.awaiting_single_date, F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_single_date(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    selected_date = message.text
    transactions = fetch_transactions(user_id, start_date=selected_date)

    filename = f"voucher_{selected_date}_{user_id}.pdf"
    generate_voucher_pdf(transactions, f"Voucher for {selected_date}", filename)
    file_input = FSInputFile(filename)
    await message.answer_document(file_input)
    await state.clear()

# Callback handler for "Select Range"
@dp.callback_query(F.data == "select_range")
async def process_select_range(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Please type the start date in the format `YYYY-MM-DD`:")
    await state.set_state(DateRangeState.awaiting_start_date)

@dp.message(DateRangeState.awaiting_start_date, F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_start_date(message: types.Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await message.answer("Please type the end date in the format `YYYY-MM-DD`:")
    await state.set_state(DateRangeState.awaiting_end_date)

@dp.message(DateRangeState.awaiting_end_date, F.text.regexp(r"^\d{4}-\d{2}-\d{2}$"))
async def handle_end_date(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    start_date = data["start_date"]
    end_date = message.text

    transactions = fetch_transactions(user_id, start_date=start_date, end_date=end_date)

    filename = f"voucher_{start_date}_to_{end_date}_{user_id}.pdf"
    generate_voucher_pdf(transactions, f"Voucher for {start_date} to {end_date}", filename)
    file_input = FSInputFile(filename)
    await message.answer_document(file_input)
    await state.clear()


@dp.message(F.text.regexp(r'/menu'))
async def show_menu(message: types.Message) -> None:
    # Build the inline keyboard with your menu items and confirmation buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 View Price List", callback_data="price_list")],
        [InlineKeyboardButton(text="💎 Top-up Instructions", callback_data="topup_instructions")],
        [InlineKeyboardButton(text="⚖️ Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton(text="📖 View Top-up History", callback_data="view_history")],
        [InlineKeyboardButton(text="📖 View Voucher List", callback_data="voucher")],
        # Row for confirmation buttons
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="confirm_no")
        ]
    ])

    await message.answer(
        "<b>🏷️ Commands Menu:</b>\n\n"
        "<b>🎯 Quick Actions:</b>\n"
        "<i>Use the buttons below for faster navigation!</i>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.in_(["confirm_yes", "confirm_no"]))
async def process_confirmation(callback_query: types.CallbackQuery) -> None:
    # Determine which confirmation was pressed
    confirm_value = 'yes' if callback_query.data == 'confirm_yes' else 'no'
    user_id = callback_query.from_user.id

    try:
        # Replace the following with your actual database update code.
        # For example:
        print(user_id)
        print(confirm_value)
        db.query("UPDATE users SET confirm_button=? WHERE user_id=?", (confirm_value, user_id))
        print(f"Updating user {user_id} confirmation to: {confirm_value}")

        await callback_query.answer(f"Your confirmation has been set to '{confirm_value}'.")
    except Exception as e:
        # Log the error or notify the user as needed
        await callback_query.answer("An error occurred while updating your confirmation.", show_alert=True)







@dp.callback_query(F.data == "topup_instructions")
async def topup_instructions_callback(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.answer(
         "💎 <code>.b userid(zoneid) diamonds</code> — <i>Top up for Brazil Region</i>.\n"
        "💎 <code>.p userid(zoneid) diamonds</code> — <i>Top up for Philippines Region (PH)</i>.\n"
         "💎 <code>.b userid zoneid diamonds</code> — <i>Top up for Brazil Region</i>.\n"
        "💎 <code>.p userid zoneid diamonds</code> — <i>Top up for Philippines Region (PH)</i>.\n"
        "💡 Replace `userid`, `zoneid`, and `diamonds` with appropriate values."
    )
    await callback_query.answer()







async def main() -> None:

    await bot.set_my_commands([
        BotCommand(command="/start",description="to see login"),
        BotCommand(command="/menu",description="to see menu"),
        ]
        )
    await dp.start_polling(bot)




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
