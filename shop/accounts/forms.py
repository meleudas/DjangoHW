from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Profile
from django.core.exceptions import ValidationError
import datetime

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('Ваш email')
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("Ім'я"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('Ваше ім\'я')
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("Прізвище"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('Ваше прізвище')
        })
    )
    
    # Додаткові поля з профілю
    bio = forms.CharField(
        required=False,
        label=_("Про себе"),
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('Розкажіть трохи про себе'),
            'rows': 3
        })
    )
    birth_date = forms.DateField(
        required=False,
        label=_("Дата народження"),
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'type': 'date'
        })
    )
    location = forms.CharField(
        required=False,
        label=_("Місто"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('Ваше місто')
        })
    )
    website = forms.URLField(
        required=False,
        label=_("Веб-сайт"),
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
            'placeholder': _('https://yourwebsite.com')
        })
    )
    avatar = forms.ImageField(
        required=False,
        label=_("Аватар"),
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
                'placeholder': _("Ім'я користувача")
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
                'placeholder': _('Пароль')
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all',
                'placeholder': _('Підтвердіть пароль')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Українізація текстів допомоги для паролів
        self.fields['password1'].help_text = _("Пароль не може бути схожим на ваше ім'я користувача або інші особисті дані. Має містити принаймні 8 символів.")
        self.fields['password2'].help_text = _("Введіть той самий пароль, що й вище, для підтвердження.")

    def clean_email(self):
        """Валідація email на унікальність"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Користувач з таким email вже існує."))
        return email

    def clean_birth_date(self):
        """Валідація віку (мінімум 13 років)"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 13:
                raise ValidationError(_("Вам потрібно бути старше 13 років для реєстрації."))
        return birth_date

    def clean_avatar(self):
        """Валідація аватара"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Перевірка розміру файлу (максимум 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError(_("Розмір файлу не може перевищувати 5MB."))
            
            # Перевірка типу файлу
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                raise ValidationError(_("Дозволені лише файли форматів JPG, PNG та GIF."))
        return avatar

    def save(self, commit=True):
        """Збереження користувача та профілю"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Створення чи оновлення профілю
            profile, created = Profile.objects.get_or_create(user=user)
            profile.bio = self.cleaned_data.get('bio', '')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.location = self.cleaned_data.get('location', '')
            profile.website = self.cleaned_data.get('website', '')
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data.get('avatar')
            profile.save()
        
        return user