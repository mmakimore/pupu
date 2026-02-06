"""
Утилиты и валидация ParkingBot
"""
import re
from datetime import datetime, timedelta

PHONE_REGEX = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'

def validate_name(name):
    name = name.strip()
    if len(name) < 2: return False, "❌ Имя слишком короткое (мин. 2)"
    if len(name) > 50: return False, "❌ Имя слишком длинное (макс. 50)"
    return True, name

def validate_phone(phone):
    cleaned = re.sub(r'[^\d+]', '', phone)
    if not re.match(PHONE_REGEX, phone):
        return False, "❌ Неверный формат. +7XXXXXXXXXX или 8XXXXXXXXXX"
    if cleaned.startswith('+7'): cleaned = '8' + cleaned[2:]
    elif cleaned.startswith('7') and len(cleaned) == 11: cleaned = '8' + cleaned[1:]
    if len(cleaned) != 11: return False, "❌ Номер должен содержать 11 цифр"
    return True, cleaned

def luhn_check(card):
    digits = [int(d) for d in card]
    odd = digits[-1::-2]; even = digits[-2::-2]
    total = sum(odd) + sum(d*2-9 if d*2>9 else d*2 for d in even)
    return total % 10 == 0

def validate_card(card):
    cleaned = re.sub(r'\D', '', card)
    if len(cleaned) != 16: return False, "❌ Номер карты: 16 цифр"
    from config import STRICT_CARD_VALIDATION
    if STRICT_CARD_VALIDATION and not luhn_check(cleaned):
        return False, "❌ Неверный номер карты"
    return True, cleaned

def validate_date(date_str):
    if not re.match(r'^(0[1-9]|[12]\d|3[01])\.(0[1-9]|1[0-2])\.\d{4}$', date_str):
        return False, None
    try:
        parsed = datetime.strptime(date_str, "%d.%m.%Y")
        if parsed.date() < datetime.now().date(): return False, None
        return True, parsed
    except ValueError: return False, None

def validate_time(time_str):
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_str): return False, None
    return True, time_str

def validate_spot_number(s):
    s = s.strip()
    if len(s) < 1: return False, "❌ Номер не может быть пустым"
    if len(s) > 10: return False, "❌ Максимум 10 символов"
    return True, s

def validate_license_plate(p):
    p = p.strip().upper()
    if len(p) < 2: return False, "❌ Слишком короткий"
    if len(p) > 15: return False, "❌ Слишком длинный"
    return True, p

def validate_car_brand(b):
    b = b.strip()
    if len(b) < 2: return False, "❌ Слишком короткое"
    if len(b) > 50: return False, "❌ Слишком длинное"
    return True, b

def validate_car_color(c):
    c = c.strip()
    if len(c) < 2: return False, "❌ Слишком короткий"
    if len(c) > 30: return False, "❌ Слишком длинный"
    return True, c

def format_datetime(dt):
    if isinstance(dt, str): dt = datetime.fromisoformat(dt)
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt):
    if isinstance(dt, str): dt = datetime.fromisoformat(dt)
    return dt.strftime("%d.%m.%Y")

def parse_datetime(date_str, time_str):
    try: return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
    except ValueError: return None

def get_next_days(count=7):
    today = datetime.now()
    return [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(count)]

def get_price_per_hour(hours):
    """Возвращает цену за час по тарифу"""
    from config import PRICE_TIERS, PRICE_DEFAULT
    for max_h, price in PRICE_TIERS:
        if hours <= max_h:
            return price
    return PRICE_DEFAULT

def calculate_price(start, end):
    """Считает цену по фиксированным тарифам"""
    h = (end - start).total_seconds() / 3600
    if h <= 0: return 0
    rate = get_price_per_hour(h)
    return round(rate * h)

def format_price_info():
    """Строка с тарифами для показа пользователю"""
    return (
        "💰 <b>Тарифы:</b>\n"
        "• 1-3ч → 150₽/ч\n"
        "• 4-6ч → 120₽/ч\n"
        "• 7-10ч → 90₽/ч\n"
        "• 11-24ч → 60₽/ч\n"
        "• 24ч+ → 60₽/ч"
    )

def mask_card(card):
    if card and len(card) >= 4: return f"****{card[-4:]}"
    return "—"
