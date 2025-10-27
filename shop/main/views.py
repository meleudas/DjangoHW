from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    return render(request, 'main/product-list.html', {'products': products})