from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.http import JsonResponse

from .models import Ad, Category, Favorite, Review
from .forms import AdForm, UserRegistrationForm, ReviewForm
from rest_framework import viewsets, filters
from .serializers import AdSerializer, ReviewSerializer


# ====================== АВТОРИЗАЦИЯ ======================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт {user.username} успешно создан!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('profile')   # после входа — в профиль


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('ad_list')


# ====================== ПРОФИЛЬ ======================
@login_required
def profile_view(request):
    my_ads = Ad.objects.filter(author=request.user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=request.user).select_related('ad')
    return render(request, 'profile.html', {
        'my_ads': my_ads,
        'favorites': favorites
    })


# ====================== ОБЪЯВЛЕНИЯ ======================
def ad_list_view(request, slug=None):
    ads = Ad.objects.filter(is_moderated=True)
    if slug:
        ads = ads.filter(category__slug=slug)

    q = request.GET.get('q')
    if q:
        ads = ads.filter(title__icontains=q) | ads.filter(description__icontains=q)

    sort = request.GET.get('sort')
    if sort == 'cheap':
        ads = ads.order_by('price', '-created_at')
    elif sort == 'expensive':
        ads = ads.order_by('-price', '-created_at')
    elif sort == 'free':
        ads = ads.filter(price=0).order_by('-created_at')
    else:
        ads = ads.order_by('-created_at')

    from django.core.paginator import Paginator
    page_obj = Paginator(ads, 12).get_page(request.GET.get('page'))

    favorite_uuids = set()
    if request.user.is_authenticated:
        favorite_uuids = set(
            Favorite.objects.filter(user=request.user).values_list('ad__uuid', flat=True)
        )

    return render(request, 'ad_list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'current_category': slug,
        'favorite_uuids': favorite_uuids,
    })


@login_required
def ad_create_view(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.is_moderated = False
            ad.save()
            messages.success(request, 'Объявление создано и отправлено на модерацию!')
            return redirect('profile')
    else:
        form = AdForm()
    return render(request, 'ad_form.html', {'form': form})


@login_required
def ad_update_view(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    if ad.author != request.user:
        return HttpResponseForbidden('Вы не можете редактировать чужое объявление.')
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_moderated = False  # отправить на повторную модерацию
            updated.save()
            messages.success(request, 'Объявление обновлено и отправлено на модерацию!')
            return redirect('profile')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ad_form.html', {'form': form})


@login_required
def ad_delete_view(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    if ad.author != request.user:
        return HttpResponseForbidden('Вы не можете удалить чужое объявление.')
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление удалено.')
        return redirect('profile')
    return render(request, 'ad_confirm_delete.html', {'ad': ad})


@login_required
def toggle_favorite(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    favorite, created = Favorite.objects.get_or_create(user=request.user, ad=ad)
    if not created:
        favorite.delete()
    return redirect(request.META.get('HTTP_REFERER', 'ad_list'))


# API
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.filter(is_moderated=True).order_by('-is_top', '-created_at')
    serializer_class = AdSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']


def ad_detail_view(request, pk):
    ad = get_object_or_404(Ad, uuid=pk)
    is_favorite = (
        request.user.is_authenticated and
        Favorite.objects.filter(user=request.user, ad=ad).exists()
    )
    reviews = ad.reviews.select_related('user').order_by('-created_at')
    user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None

    if request.method == 'POST' and request.user.is_authenticated:
        if user_review:
            messages.warning(request, 'Вы уже оставили отзыв на это объявление.')
            return redirect('ad_detail', pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ad = ad
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен!')
            return redirect('ad_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'ad_detail.html', {
        'ad': ad,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': form,
    })



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        ad_id = self.kwargs.get('ad_id')
        return Review.objects.filter(ad_id=ad_id)

    def perform_create(self, serializer):
        ad = get_object_or_404(Ad, id=self.kwargs['ad_id'])
        # Один отзыв на объявление от пользователя
        if Review.objects.filter(ad=ad, user=self.request.user).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв.")
        serializer.save(user=self.request.user, ad=ad)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if not review.can_edit(request.user):
            return Response({"error": "Вы можете редактировать только свой отзыв"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    

@login_required
def add_or_edit_review(request, uuid):          # ← изменили ad_uuid → uuid
    ad = get_object_or_404(Ad, uuid=uuid)
    
    # Проверяем, есть ли уже отзыв от этого пользователя
    review = Review.objects.filter(ad=ad, user=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            review_obj = form.save(commit=False)
            review_obj.ad = ad
            review_obj.user = request.user
            review_obj.save()
            
            messages.success(request, "Отзыв успешно сохранён!")
            return redirect('ad_detail', pk=ad.uuid)   # или uuid=ad.uuid
        else:
            messages.error(request, "Ошибка при сохранении отзыва")
    else:
        form = ReviewForm(instance=review)
    
    # Передаём всё необходимое в шаблон
    return render(request, 'ad_detail.html', {
        'ad': ad,
        'review_form': form,
        'reviews': ad.reviews.select_related('user').order_by('-created_at'),
        'user_review': review,
        'is_favorite': request.user.is_authenticated and Favorite.objects.filter(user=request.user, ad=ad).exists(),
    })


@login_required
def reveal_phone(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    
    # Показываем телефон только если он указан в профиле автора
    phone = None
    try:
        if hasattr(ad.author, 'profile') and ad.author.profile.phone:
            phone = ad.author.profile.phone
        else:
            # Если Profile модели нет или телефон не заполнен
            phone = "Телефон не указан"
    except:
        phone = "Телефон не указан"
    
    return JsonResponse({'phone': phone})