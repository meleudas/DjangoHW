
from django.contrib import admin
from django.utils.html import format_html, escape
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'author_link', 'product_link', 'rating_stars', 'title_preview',
        'created_at', 'is_active', 'helpful_count'
    ]
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = [
        'author__username', 'product__name', 'title', 'content'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    actions = ['activate_reviews', 'deactivate_reviews']
    fieldsets = (
        ('Основне', {
            'fields': ('product', 'author', 'rating', 'title', 'content')
        }),
        ('Деталі', {
            'fields': ('advantages', 'disadvantages'),
            'classes': ('collapse',)
        }),
        ('Модерація', {
            'fields': ('is_active', 'helpful_count', 'created_at', 'updated_at')
        }),
    )

    def author_link(self, obj):
        url = admin.reverse("admin:auth_user_change", args=[obj.author_id])
        return format_html('<a href="{}">{}</a>', url, escape(obj.author.username))
    author_link.short_description = 'Автор'
    author_link.admin_order_field = 'author__username'

    def product_link(self, obj):
        url = admin.reverse("admin:main_product_change", args=[obj.product_id])
        return format_html('<a href="{}">{}</a>', url, escape(obj.product.name))
    product_link.short_description = 'Товар'
    product_link.admin_order_field = 'product__name'

    def rating_stars(self, obj):
        return format_html('<span style="color: gold;">{}</span>', obj.get_rating_display_stars())
    rating_stars.short_description = 'Рейтинг'

    def title_preview(self, obj):
        return escape(obj.title[:50] + '…' if len(obj.title) > 50 else obj.title)
    title_preview.short_description = 'Заголовок'

    @admin.action(description="Активувати вибрані відгуки")
    def activate_reviews(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активовано {updated} відгук(ів).')

    @admin.action(description="Деактивувати вибрані відгуки")
    def deactivate_reviews(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивовано {updated} відгук(ів).')