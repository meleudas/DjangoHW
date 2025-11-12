from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from django.db.models import Avg, Count
from django.core.cache import cache
from discounts.models import Discount

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product_list_by_category', args=[self.slug])


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    detailed_description = MarkdownxField(
        blank=True,
        help_text=_("Детальний опис товару в форматі Markdown")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product_detail', args=[self.id, self.slug])

    # --- Методи для знижок ---
    def get_active_discount(self, quantity=1):
        """Повертає найкращу активну знижку для товару або None"""
        discounts = self.discounts.filter(is_active=True)
        valid_discounts = [d for d in discounts if d.is_valid() and quantity >= d.min_quantity]
        if not valid_discounts:
            return None
        # вибираємо максимальну за сумою знижки
        best = max(valid_discounts, key=lambda d: d.calculate_discount(self.price, quantity))
        return best

    def get_discounted_price(self, quantity=1):
        discount = self.get_active_discount(quantity)
        if discount:
            return discount.get_discounted_price(self.price, quantity)
        return self.price

    def has_active_discount(self):
        return self.get_active_discount() is not None

    def get_discount_percentage(self):
        """Повертає відсоток знижки для badge, якщо є"""
        discount = self.get_active_discount()
        if not discount:
            return 0
        if discount.discount_type == 'percentage':
            return discount.value
        elif discount.discount_type == 'fixed':
            return round((discount.value / self.price) * 100, 1)
        return 0

    # --- Методи для рейтингів та відгуків ---
    def get_average_rating(self):
        cache_key = f'product_{self.id}_avg_rating'
        avg = cache.get(cache_key)
        if avg is None:
            avg = self.reviews.filter(is_active=True).aggregate(avg=Avg('rating'))['avg'] or 0.0
            avg = round(avg, 1)
            cache.set(cache_key, avg, 300)
        return avg

    def get_reviews_count(self):
        return self.reviews.filter(is_active=True).count()

    def get_rating_distribution(self):
        cache_key = f'product_{self.id}_rating_dist'
        dist = cache.get(cache_key)
        if dist is None:
            reviews = self.reviews.filter(is_active=True)
            dist = {i: 0 for i in range(1, 6)}
            dist.update(
                reviews.values('rating')
                       .annotate(count=Count('rating'))
                       .values_list('rating', 'count')
            )
            cache.set(cache_key, dist, 300)
        return dist
