from django import template
from main.models import Product

register = template.Library()

@register.simple_tag
def get_products_count(category=None):
    """Повертає кількість товарів у категорії"""
    if category:
        return Product.objects.filter(category=category, is_available=True).count()
    return Product.objects.filter(is_available=True).count()

@register.simple_tag
def calculate_total(price, quantity):
    """Обчислює загальну вартість"""
    try:
        return float(price) * int(quantity)
    except (ValueError, TypeError):
        return 0

@register.simple_tag(takes_context=True)
def user_greeting(context):
    """Повертає привітання на основі контексту"""
    user = context.get('user')
    if user and user.is_authenticated:
        return f"Вітаємо, {user.username}!"
    return "Вітаємо, гість!"

# --- Inclusion Tags ---

@register.inclusion_tag('main/components/product_card.html')
def show_product_card(product):
    """Відображає картку товару (без знижок)"""
    return {
        'product': product,
    }

@register.inclusion_tag('main/components/popular_products.html')
def show_popular_products(count=4):
    """Відображає список популярних товарів"""
    products = Product.objects.filter(is_available=True).order_by('-views')[:count]
    return {'popular_products': products}