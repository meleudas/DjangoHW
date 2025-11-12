from django.contrib import admin
from .models import Discount, PromoCode, PromoCodeUsage
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'is_valid_now')
    list_filter = ('discount_type', 'is_active', 'start_date')
    search_fields = ('product__name', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)
    date_hierarchy = 'start_date'
    actions = ['activate_discounts', 'deactivate_discounts']

    def is_valid_now(self, obj):
        return obj.is_valid()
    is_valid_now.boolean = True
    is_valid_now.short_description = 'Дійсна зараз'

    def activate_discounts(self, request, queryset):
        queryset.update(is_active=True)
    activate_discounts.short_description = "Активувати вибрані знижки"

    def deactivate_discounts(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_discounts.short_description = "Деактивувати вибрані знижки"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'usage_progress', 'valid_period', 'is_active', 'created_by')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    fieldsets = (
        (None, {'fields': ('code', 'discount_type', 'value', 'description')}),
        ('Дати та обмеження', {'fields': ('start_date', 'end_date', 'usage_limit', 'used_count', 'min_order_amount', 'is_active')}),
        ('Інше', {'fields': ('created_by', 'created_at')}),
    )
    actions = ['activate_codes', 'deactivate_codes', 'reset_usage']

    def usage_progress(self, obj):
        if obj.usage_limit:
            percent = int((obj.used_count / obj.usage_limit) * 100) if obj.usage_limit else 0
            return format_html('<progress value="{}" max="100"></progress> {}%', percent, percent)
        return f"{obj.used_count}"
    usage_progress.short_description = 'Використано'

    def valid_period(self, obj):
        return f"{obj.start_date:%d.%m.%Y} — {obj.end_date:%d.%m.%Y}"
    valid_period.short_description = 'Період дії'

    def activate_codes(self, request, queryset):
        queryset.update(is_active=True)
    activate_codes.short_description = "Активувати коди"

    def deactivate_codes(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_codes.short_description = "Деактивувати коди"

    def reset_usage(self, request, queryset):
        queryset.update(used_count=0)
    reset_usage.short_description = "Скинути лічильник використань"


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promo_code')
    search_fields = ('user__username', 'promo_code__code')
    readonly_fields = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    date_hierarchy = 'used_at'
