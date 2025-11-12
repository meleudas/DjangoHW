# reviews/forms.py
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'advantages', 'disadvantages']
        widgets = {
            'rating': forms.RadioSelect(
                attrs={
                    'class': 'hidden',  # Ми використовуємо власний віджет
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    'placeholder': 'Короткий, але змістовний заголовок (мін. 5 символів)',
                    'required': True
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    'rows': 5,
                    'placeholder': 'Розкажіть детальніше про ваш досвід (мін. 20 символів)',
                    'required': True
                }
            ),
            'advantages': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    'rows': 3,
                    'placeholder': 'Що вам сподобалось? (необов’язково)'
                }
            ),
            'disadvantages': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                    'rows': 3,
                    'placeholder': 'Що можна покращити? (необов’язково)'
                }
            ),
        }
        labels = {
            'rating': 'Ваша оцінка',
            'title': 'Заголовок',
            'content': 'Основний текст',
            'advantages': 'Переваги',
            'disadvantages': 'Недоліки',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 5:
            raise forms.ValidationError('Заголовок має містити щонайменше 5 символів.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 20:
            raise forms.ValidationError('Текст відгуку має містити щонайменше 20 символів.')
        return content

    def clean_advantages(self):
        return self.cleaned_data.get('advantages', '').strip()

    def clean_disadvantages(self):
        return self.cleaned_data.get('disadvantages', '').strip()