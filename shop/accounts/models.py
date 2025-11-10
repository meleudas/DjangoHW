from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_("Користувач"),
        related_name='profile'
    )
    bio = models.TextField(
        blank=True, 
        verbose_name=_("Біографія")
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/', 
        blank=True, 
        verbose_name=_("Аватар")
    )
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Дата народження")
    )
    location = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Місто")
    )
    website = models.URLField(
        blank=True, 
        verbose_name=_("Веб-сайт")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Створено")
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_("Оновлено")
    )

    class Meta:
        verbose_name = _("Профіль")
        verbose_name_plural = _("Профілі")
        ordering = ['-created_at']

    def __str__(self):
        return f"Профіль користувача {self.user.username}"

    def has_avatar(self):
        """Повертає, чи є у користувача аватар"""
        return bool(self.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = _("Є аватар")