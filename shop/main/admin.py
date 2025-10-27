from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_available', 'created_at')
    ordering = ('-created_at',)