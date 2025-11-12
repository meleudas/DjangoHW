from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from .forms import CartAddProductForm
from main.models import Product
from django.views.decorators.http import require_POST


@require_POST
def create_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # Додаємо форму оновлення кількості для кожного товару
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )
    # Отримуємо інфо про промокод (для шаблону)
    promo_info = cart.get_promo_info()
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'promo_info': promo_info,  # ← передаємо в шаблон
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('cart:cart_detail')


