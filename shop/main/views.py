from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from cart.forms import CartAddProductForm 

def product_list(request, category_slug=None):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_available=True)

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # 🔍 Пошук
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # 📊 Сортування
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

    # 📄 Пагінація (6 товарів на сторінку)
    paginator = Paginator(products, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'categories': categories,
        'category': category,
        'current_sort': sort,
        'search_query': search_query,
    }
    return render(request, 'main/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    product.views += 1
    product.save(update_fields=['views'])
    
    cart_product_form = CartAddProductForm()

    # Схожі товари
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    # --- Новий блок: відгуки ---
    reviews = product.reviews.filter(is_active=True)
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(author=request.user).first()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'cart_product_form': cart_product_form,
        'reviews_count': product.get_reviews_count(),
        'average_rating': product.get_average_rating(),
        'rating_distribution': product.get_rating_distribution(),
        'user_review': user_review,
    }
    return render(request, 'main/product_detail.html', context)