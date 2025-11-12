# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from main.models import Product


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 зірка'),
        (2, '2 зірки'),
        (3, '3 зірки'),
        (4, '4 зірки'),
        (5, '5 зірок'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Товар')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Автор')
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Рейтинг')
    )
    title = models.CharField(
        max_length=100,
        verbose_name=_('Заголовок')
    )
    content = models.TextField(
        max_length=1000,
        verbose_name=_('Текст відгуку')
    )
    advantages = models.TextField(
        blank=True,
        verbose_name=_('Переваги')
    )
    disadvantages = models.TextField(
        blank=True,
        verbose_name=_('Недоліки')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Створено')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Оновлено')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активний')
    )
    helpful_count = models.IntegerField(
        default=0,
        verbose_name=_('Кількість "Корисно"')
    )

    class Meta:
        verbose_name = _('Відгук')
        verbose_name_plural = _('Відгуки')
        ordering = ['-created_at']
        unique_together = ('product', 'author')

    def __str__(self):
        return f'{self.title} — {self.author.username}'

    def get_rating_display_stars(self):
        """Повертає HTML-рядок з зірками (наприклад, ★★★★☆)"""
        full = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return f'{full}{empty}'