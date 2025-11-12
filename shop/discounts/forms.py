from django import forms
from .models import Discount, PromoCode
from django.utils import timezone
from decimal import Decimal

class DiscountForm(forms.ModelForm):
    start_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Discount
        fields = ['discount_type', 'value', 'start_date', 'end_date', 'min_quantity', 'description']
        widgets = {
            'discount_type': forms.RadioSelect(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_value(self):
        v = self.cleaned_data.get('value')
        dtype = self.cleaned_data.get('discount_type')
        if dtype == 'percentage':
            if v < 0 or v > 100:
                raise forms.ValidationError("Відсоток має бути між 0 та 100.")
        else:
            if v <= 0:
                raise forms.ValidationError("Фіксована сума має бути більшою за 0.")
        return v

    def clean_min_quantity(self):
        mq = self.cleaned_data.get('min_quantity')
        if mq < 1:
            raise forms.ValidationError("Мінімальна кількість має бути принаймні 1.")
        return mq

    def clean(self):
        cleaned = super().clean()
        sd = cleaned.get('start_date')
        ed = cleaned.get('end_date')
        if sd and ed and ed <= sd:
            raise forms.ValidationError("Дата завершення має бути після дати початку.")
        return cleaned


# forms.py — лише оновлення PromoCodeForm (DiscountForm залишив як є)

class PromoCodeForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
        })
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
        })
    )

    class Meta:
        model = PromoCode
        fields = ['code', 'discount_type', 'value', 'start_date', 'end_date', 'usage_limit', 'min_order_amount', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500',
                'placeholder': 'Наприклад: SAVE10'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'step': '0.01'
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Залиште порожнім для необмеженого'
            }),
            'min_order_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Необов’язково'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper().replace(' ', '')
        if len(code) < 4:
            raise forms.ValidationError('Код має містити мінімум 4 символи.')
        # Унікальність перевіряється ModelForm автоматично (бо code — unique)
        return code

    def clean_value(self):
        v = self.cleaned_data.get('value')
        dtype = self.cleaned_data.get('discount_type')
        if dtype == 'percentage':
            if v < Decimal('0') or v > Decimal('100'):
                raise forms.ValidationError('Відсоток має бути між 0 та 100.')
        elif dtype == 'fixed':
            if v <= Decimal('0'):
                raise forms.ValidationError('Фіксована сума має бути більшою за 0.')
        return v

    def clean_usage_limit(self):
        lim = self.cleaned_data.get('usage_limit')
        if lim is not None and lim <= 0:
            raise forms.ValidationError('Ліміт має бути більше 0.')
        return lim

    def clean(self):
        cleaned = super().clean()
        sd = cleaned.get('start_date')
        ed = cleaned.get('end_date')
        
        
        if sd and ed:
            if ed <= sd:
                raise forms.ValidationError("Дата завершення має бути після дати початку.")
       
        
        return cleaned

class ApplyPromoCodeForm(forms.Form):
    promo_code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'placeholder': 'Введіть промокод',
        'class': 'input-class'  # додай Tailwind класи у шаблоні
    }))

    def clean_promo_code(self):
        code = self.cleaned_data.get('promo_code', '').strip().upper().replace(' ', '')
        if not code:
            raise forms.ValidationError('Введіть код.')
        # не робимо DB lookup тут — зробимо у view
        return code
