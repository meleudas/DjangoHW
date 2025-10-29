from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name='currency')
def format_currency(value, currency='грн'):
    """Форматує число як ціну з валютою"""
    try:
        return f"{float(value):.2f} {currency}"
    except (ValueError, TypeError):
        return value

@register.filter
def discount_percentage(original_price, discount_price):
    """Обчислює відсоток знижки"""
    try:
        original = float(original_price)
        discount = float(discount_price)
        if original <= 0:
            return 0
        percentage = ((original - discount) / original) * 100
        return int(percentage)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def compact_number(value):
    """Скорочує великі числа: 1000 → 1K, 1500000 → 1.5M"""
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value / 1000000:.1f}M"
        elif value >= 1000:
            return f"{value / 1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value

@register.filter
def time_ago(date):
    """Відображає час у форматі 'назад'"""
    if not date:
        return ""

    now = timezone.now()
    diff = now - date
    seconds = diff.total_seconds()

    if seconds < 60:
        return "щойно"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} хв тому"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} год тому"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} дн тому"
    else:
        return date.strftime("%d.%m.%Y")    