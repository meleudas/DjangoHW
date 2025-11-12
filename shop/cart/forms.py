from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1, widget=forms.NumberInput(
        attrs={ 'class': 'p-3 border-2 border-gray-400 rounded-lg w-20 text-center font-bold '
            'text-gray-900 bg-white focus:border-blue-500 focus:outline-none',
            'placeholder': '1',
        }))
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
