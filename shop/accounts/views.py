from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from main.models import Category

def get_categories():
    return Category.objects.filter(is_active=True)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url) if next_url else redirect('main:product_list')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'categories': get_categories()
    })

def logout_view(request):
    logout(request)
    return redirect('main:product_list')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:product_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:product_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'categories': get_categories()
    })

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'categories': get_categories()
    })