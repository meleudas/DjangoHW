from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

DISCOUNT_TYPES = (
    ('percentage', 'Відсоток'),
    ('fixed', 'Фіксована сума'),
)

PROMO_TYPES = (
    ('percentage', 'Відсоток'),
    ('fixed', 'Фіксована сума'),
    ('free_shipping', 'Безкоштовна доставка'),
)


class Discount(models.Model):
    product = models.ForeignKey('main.Product', related_name='discounts', on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Знижка'
        verbose_name_plural = 'Знижки'

    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.value}% на {self.product}"
        return f"-{self.value} грн на {self.product}"

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def clean(self):
        # валідація полів
        if self.discount_type == 'percentage':
            if self.value < 0 or self.value > 100:
                raise ValidationError({'value': 'Для відсоткової знижки значення має бути від 0 до 100.'})
        else:
            # fixed
            if self.value <= 0:
                raise ValidationError({'value': 'Фіксована знижка повинна бути більшою за 0.'})
        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'Дата завершення повинна бути після дати початку.'})
        if self.min_quantity < 1:
            raise ValidationError({'min_quantity': 'Мінімальна кількість повинна бути не менше 1.'})

    def calculate_discount(self, price, quantity=1):
        """
        Повертає суму знижки (Decimal) для заданої ціни та кількості.
        Дотримуємось округлення до 2 десяткових.
        """
        price = Decimal(price)
        quantity = int(quantity)
        if quantity < self.min_quantity:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            amount = (price * (Decimal(self.value) / Decimal('100'))) * quantity
        else:
            # fixed: фіксована на одиницю товару або на замовлення? будемо вважати на одиницю
            amount = Decimal(self.value) * quantity
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_discounted_price(self, price, quantity=1):
        """Повертає (price * quantity) - discount_amount."""
        total = (Decimal(price) * int(quantity))
        discount_amount = self.calculate_discount(price, quantity)
        discounted = total - discount_amount
        return max(discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), Decimal('0.00'))


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=PROMO_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоди'

    def __str__(self):
        return self.code

    def clean(self):
        # нормалізація коду та валідація
        if not self.code or len(self.code.strip()) < 4:
            raise ValidationError({'code': 'Код має містити мінімум 4 символи.'})
        self.code = self.code.strip().upper().replace(' ', '')
        if self.discount_type in ('percentage',) and (self.value < 0 or self.value > 100):
            raise ValidationError({'value': 'Для відсоткового типу значення має бути 0-100.'})
        if self.discount_type == 'fixed' and self.value <= 0:
            raise ValidationError({'value': 'Фіксована сума має бути більшою за 0.'})
        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'Дата завершення повинна бути після дати початку.'})
        if self.usage_limit is not None and self.usage_limit <= 0:
            raise ValidationError({'usage_limit': 'Ліміт використань повинен бути більше 0 або залиште порожнім.'})

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.start_date <= now <= self.end_date):
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def can_be_used(self):
        return self.is_valid()

    def apply_discount(self, order_amount):
        """
        Повертає tuple (discount_amount: Decimal, new_total: Decimal, note: str)
        Для free_shipping — повертаємо discount_amount=0 і note='free_shipping'
        """
        order_amount = Decimal(order_amount)
        note = ''
        discount_amount = Decimal('0.00')
        if not self.is_valid():
            return Decimal('0.00'), order_amount, 'invalid'
        if order_amount < self.min_order_amount:
            return Decimal('0.00'), order_amount, 'min_amount_not_met'
        if self.discount_type == 'percentage':
            discount_amount = (order_amount * (Decimal(self.value) / Decimal('100'))).quantize(Decimal('0.01'))
        elif self.discount_type == 'fixed':
            discount_amount = min(Decimal(self.value), order_amount).quantize(Decimal('0.01'))
        elif self.discount_type == 'free_shipping':
            note = 'free_shipping'
            discount_amount = Decimal('0.00')
        new_total = max((order_amount - discount_amount).quantize(Decimal('0.01')), Decimal('0.00'))
        return discount_amount, new_total, note

    def increment_usage(self):
        self.used_count = models.F('used_count') + 1
        self.save(update_fields=['used_count'])
        # refresh from db to get numeric value
        self.refresh_from_db()
    
    def is_valid_for_application(self, now=None):
        """Перевірка, чи можна застосувати промокод зараз (до створення замовлення)"""
        if now is None:
            now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if self.usage_limit is not None:
            used = self.usages.count()
            if used >= self.usage_limit:
                return False
        return True

    def apply_discount(self, amount):
        """Повертає (discount_amount, new_total, note) без збереження"""
        amount = Decimal(amount)
        if self.discount_type == 'percentage':
            discount = (amount * self.value) / Decimal('100')
            discount = min(discount, amount)
            note = f"{self.value}% знижки"
        elif self.discount_type == 'fixed':
            discount = min(self.value, amount)
            note = f"−{self.value} грн"
        else:
            discount = Decimal('0.00')
            note = "Невідомий тип"
        new_total = amount - discount
        return discount, new_total, note


# Переконайтеся, що у PromoCodeUsage є:
class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # 👇 додаємо order_amount
    order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Сума замовлення на момент застосування промокоду"
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.promo_code.code} використано {self.user or 'анонімом'}"

    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Використання промокоду'
        verbose_name_plural = 'Використання промокодів'

