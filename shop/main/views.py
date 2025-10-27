from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Product, Category

def product_list(request, category_slug=None):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_available=True)

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Сортування
    sort = request.GET.get('sort', 'new')
    sort_mapping = {
        'new': '-created_at',
        'old': 'created_at',
        'popular': '-views',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
    }
    products = products.order_by(sort_mapping.get(sort, '-created_at'))

    context = {
        'products': products,
        'categories': categories,
        'category': category,
        'current_sort': sort,
    }
    return render(request, 'main/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    product.views += 1
    product.save(update_fields=['views'])

    # Схожі товари (4 шт.)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'main/product_detail.html', context)