from django import template
from django.utils import timezone
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe
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
    
@register.filter(name='markdown')
def markdown_format(text):
    """Конвертує Markdown текст у HTML"""
    if not text:
        return ""
    return mark_safe(markdownify(text))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def rjust(value, width):
    return str(value).rjust(width)

@register.filter
def ljust(value, width):
    return str(value).ljust(width)

@register.filter
def stars_display(rating):
    """Відображає рейтинг зірками (HTML)"""
    try:
        rating = int(round(float(rating)))
        filled = '★' * rating
        empty = '☆' * (5 - rating)
        return mark_safe(filled + empty)
    except (ValueError, TypeError):
        return mark_safe('☆☆☆☆☆')

@register.filter
def stars_display_for_choice(choice_value, selected_value):
    """
    Повертає HTML для однієї зірки на основі choice_value та selected_value.
    Використовується для радіо-кнопок.
    """
    try:
        choice_value = int(choice_value)
        selected_value = int(selected_value) if selected_value else 0
        # Якщо це вибране значення або менше за вибране, то зірка заповнена
        is_filled = choice_value <= selected_value
        return mark_safe('★' if is_filled else '☆')
    except (ValueError, TypeError):
        return mark_safe('☆')
    
    
@register.filter(name='replace')
def replace(value, args):
    """Замінює підрядок у рядку: {{ value|replace:"старе,нове" }}"""
    try:
        old, new = args.split(',', 1)
        return value.replace(old, new)
    except Exception:
        return value
