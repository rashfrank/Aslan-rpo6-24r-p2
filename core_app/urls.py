from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_view, 
    CustomLoginView, 
    logout_view,
    profile_view, 
    ad_list_view, 
    ad_create_view,
    AdViewSet, 
    toggle_favorite, 
    ad_update_view, 
    ad_delete_view,
    ad_detail_view,
    reveal_phone,
    add_or_edit_review,   # ← добавили этот импорт
)

router = DefaultRouter()
router.register(r'ads', AdViewSet)

urlpatterns = [
    path('', ad_list_view, name='ad_list'),
    path('category/<slug:slug>/', ad_list_view, name='category_list'),

    # Авторизация
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    # Объявления
    path('ad/new/', ad_create_view, name='ad_create'),
    path('ad/<uuid:uuid>/edit/', ad_update_view, name='ad_update'),
    path('ad/<uuid:uuid>/delete/', ad_delete_view, name='ad_delete'),
    path('profile/', profile_view, name='profile'),

    # Детальная страница объявления
    path('ad/<uuid:pk>/', ad_detail_view, name='ad_detail'),

    # Избранное
    path('ad/<uuid:uuid>/favorite/', toggle_favorite, name='toggle_favorite'),

    # Отзывы (исправленная строка)
    path('ad/<uuid:uuid>/review/', add_or_edit_review, name='add_or_edit_review'),

    # API
    path('api/', include(router.urls)),
    path('ad/<uuid:uuid>/reveal-phone/', reveal_phone, name='reveal_phone'),
]