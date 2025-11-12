from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Review
from .forms import ReviewForm
from main.models import Product


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Перевіряємо, чи користувач уже залишав відгук
    existing = Review.objects.filter(product=product, author=request.user).first()
    if existing:
        messages.warning(request, 'Ви вже залишили відгук на цей товар.')
        return redirect('main:product_detail', id=product.id, slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            messages.success(request, 'Відгук успішно додано.')
            return redirect('main:product_detail', id=product.id, slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'product': product,
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author != request.user:
        return HttpResponseForbidden("Ви не можете редагувати чужий відгук.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Відгук оновлено.')
            return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Ви не можете видалити цей відгук.")

    product = review.product
    review.delete()
    messages.success(request, 'Відгук видалено.')
    return redirect('main:product_detail', id=product.id, slug=product.slug)


@login_required
def mark_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id, is_active=True)
    review.helpful_count += 1
    review.save(update_fields=['helpful_count'])
    messages.success(request, 'Дякуємо за відгук!')
    return redirect(request.META.get('HTTP_REFERER', 'main:product_list'))