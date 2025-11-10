from django.contrib import admin
from django.utils.html import format_html
from markdownx.admin import MarkdownxModelAdmin 
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'is_active', 'image_tag')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "—"
    image_tag.short_description = 'Зображення'


@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):  
    list_display = ('id', 'name', 'category', 'price', 'is_available', 'featured', 'views', 'image_tag')
    list_filter = ('category', 'is_available', 'featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_available', 'featured')
    ordering = ('-created_at',)

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'image')
        }),
        ('Описи', {
            'fields': ('description', 'detailed_description'),  
            'description': "Короткий опис — звичайний текст. Детальний опис — у форматі Markdown."
        }),
        ('Ціни та доступність', {
            'fields': ('price', 'is_available', 'featured')
        }),
        ('Статистика та службове', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',) 
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'views')  

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "—"
    image_tag.short_description = 'Зображення'