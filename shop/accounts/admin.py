from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Profile

class ProfileInline(admin.StackedInline):
    """Вбудована форма профілю у адмінці користувачів"""
    model = Profile
    can_delete = False
    verbose_name = _("Профіль")
    verbose_name_plural = _("Профілі")
    classes = ('collapse',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('bio', 'avatar', 'birth_date', 'location', 'website')
        }),
        (_("Системна інформація"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CustomUserAdmin(UserAdmin):
    """Розширена адмін-панель користувачів"""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_location', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__location')
    
    def get_location(self, obj):
        """Отримання міста з профілю"""
        return obj.profile.location if hasattr(obj, 'profile') and obj.profile.location else "-"
    get_location.short_description = _("Місто")
    get_location.admin_order_field = 'profile__location'

class ProfileAdmin(admin.ModelAdmin):
    """Адмін-панель для профілів"""
    list_display = ('user', 'location', 'birth_date', 'has_avatar', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location', 'bio')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    fieldsets = (
        (_("Користувач"), {
            'fields': ('user', 'avatar', 'avatar_preview')
        }),
        (_("Основна інформація"), {
            'fields': ('bio', 'birth_date', 'location', 'website')
        }),
        (_("Системна інформація"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avatar_preview(self, obj):
        """Попередній перегляд аватара в адмінці"""
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="100" height="100" class="rounded-lg object-cover" />')
        return _("Немає аватара")
    avatar_preview.short_description = _("Попередній перегляд")

# Перереєстрація моделі User з розширеною адмін-панеллю
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)