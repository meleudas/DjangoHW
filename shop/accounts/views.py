from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from main.models import Category
from django.core.exceptions import ValidationError

def get_categories():
    return Category.objects.filter(is_active=True)

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _("Ви успішно увійшли до системи!"))
            next_url = request.GET.get('next')
            return redirect(next_url) if next_url else redirect('main:product_list')
        else:
            messages.error(request, _("Неправильне ім'я користувача або пароль."))
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'categories': get_categories()
    })

def logout_view(request):
    username = request.user.username
    logout(request)
    messages.info(request, _(f"Користувач {username} успішно вийшов з системи."))
    return redirect('main:product_list')

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, _("Ви вже авторизовані."))
        return redirect('main:product_list')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                # Автоматична авторизація після реєстрації
                login(request, user)
                messages.success(request, _("Реєстрація успішна! Ви увійшли до системи."))
                return redirect('main:product_list')
            except ValidationError as e:
                form.add_error(None, str(e))
            except Exception as e:
                messages.error(request, _("Виникла помилка при реєстрації: ") + str(e))
        else:
            messages.error(request, _("Будь ласка, виправте помилки у формі."))
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'categories': get_categories()
    })

@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile,
        'categories': get_categories()
    })