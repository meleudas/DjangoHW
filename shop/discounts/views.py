# discounts/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from .models import Discount, PromoCode, PromoCodeUsage
from main.models import Product
from .forms import DiscountForm, PromoCodeForm, ApplyPromoCodeForm


# =============== Discount Views (без змін) ===============
def product_discounts(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    now = timezone.now()
    active = product.discounts.filter(is_active=True, start_date__lte=now, end_date__gte=now)
    best = None
    price = product.price
    best_amount = Decimal('0.00')
    for d in active:
        amt = d.calculate_discount(price, quantity=1)
        if amt > best_amount:
            best_amount = amt
            best = d
    return render(request, 'discounts/product_discounts.html', {
        'product': product,
        'active_discounts': active,
        'best': best
    })


@staff_member_required
def add_discount(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            disc = form.save(commit=False)
            disc.product = product
            disc.save()
            return redirect(product.get_absolute_url())
    else:
        form = DiscountForm()
    return render(request, 'discounts/add_discount.html', {
        'form': form,
        'product': product
    })


@staff_member_required
def edit_discount(request, discount_id):
    disc = get_object_or_404(Discount, pk=discount_id)
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=disc)
        if form.is_valid():
            form.save()
            return redirect(disc.product.get_absolute_url())
    else:
        form = DiscountForm(instance=disc)
    return render(request, 'discounts/edit_discount.html', {
        'form': form,
        'discount': disc
    })


@staff_member_required
def delete_discount(request, discount_id):
    disc = get_object_or_404(Discount, pk=discount_id)
    product_url = disc.product.get_absolute_url()
    disc.delete()
    return redirect(product_url)


# =============== PromoCode Views ===============
@staff_member_required
def promo_code_list(request):
    qs = PromoCode.objects.all()
    q = request.GET.get('q')
    status = request.GET.get('status')
    if q:
        qs = qs.filter(code__icontains=q)
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)
    return render(request, 'discounts/promo_code_list.html', {'codes': qs})


@staff_member_required
def create_promo_code(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            pc = form.save(commit=False)
            pc.code = pc.code.strip().upper().replace(' ', '')
            pc.save()
            return redirect('discounts:promo_code_list')
    else:
        form = PromoCodeForm()
    return render(request, 'discounts/promo_code_form.html', {'form': form})
    


@staff_member_required
def edit_promo_code(request, promo_id):
    promo = get_object_or_404(PromoCode, pk=promo_id)
    if request.method == 'POST':
        form = PromoCodeForm(request.POST, instance=promo)
        if form.is_valid():
            pc = form.save(commit=False)
            pc.code = pc.code.strip().upper().replace(' ', '')
            pc.save()
            return redirect('discounts:promo_code_list')
    else:
        form = PromoCodeForm(instance=promo)
    return render(request, 'discounts/promo_code_form.html', {
        'form': form,
        'promo': promo
    })


@staff_member_required
def promo_code_stats(request, code_id):
    promo = get_object_or_404(PromoCode, pk=code_id)
    usages = promo.usages.select_related('user').all()
    total_discount = usages.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
    return render(request, 'discounts/promo_code_stats.html', {
        'promo': promo,
        'usages': usages,
        'total_discount': total_discount
    })


# =============== Promo Application (для користувачів) ===============
@login_required
@require_POST
def apply_promo_code(request):
    form = ApplyPromoCodeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    code = form.cleaned_data['promo_code']
    order_amount = request.POST.get('order_amount', '0')
    try:
        order_amount = Decimal(order_amount)
    except (ValueError, TypeError):
        order_amount = Decimal('0.00')

    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return JsonResponse({'error': 'Промокод не знайдено'}, status=404)

    # Валідація без запису у БД
    if not promo.is_valid_for_application():
        return JsonResponse({'error': 'Промокод недійсний або вичерпано ліміт'}, status=400)

    if order_amount < promo.min_order_amount:
        return JsonResponse({
            'error': f'Мінімальна сума замовлення — {promo.min_order_amount} грн'
        }, status=400)

    discount_amount, new_total, note = promo.apply_discount(order_amount)

    # Зберігаємо ID у сесію
    request.session['applied_promo'] = promo.id
    # Опціонально: зберігаємо код і note для відображення
    request.session['applied_promo_code'] = promo.code
    request.session['promo_note'] = note

    return JsonResponse({
        'success': True,
        'code': promo.code,
        'discount_amount': str(discount_amount),
        'new_total': str(new_total),
        'note': note,
    })


@login_required
def remove_promo_code(request):
    request.session.pop('applied_promo', None)
    request.session.pop('applied_promo_code', None)
    request.session.pop('promo_note', None)
    return redirect(request.GET.get('next', '/'))