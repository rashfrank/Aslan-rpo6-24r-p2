import uuid
from django.db import models
from django.contrib.auth.models import User
from pytils.translit import slugify
from django.db.models import Avg
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255,)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Изображение")
    slug = models.SlugField(max_length=255, unique=True, blank=True,)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class City(models.Model):
    name = models.CharField(max_length=100,)

    def __str__(self):
        return self.name
    

class Ad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads', verbose_name="Категория")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='ads', verbose_name="Город")

    title = models.CharField(max_length=255, )
    description = models.TextField()
    price = models.PositiveBigIntegerField(verbose_name="Цена( в тенге )", help_text="Укажите 0, если бесплатно")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, verbose_name="Изображение")
   
    update_at = models.DateTimeField(auto_now=True)

    is_moderated = models.BooleanField(default=False, verbose_name="Прошло модерацию")

    is_top = models.BooleanField(
        default=False,
        verbose_name="Топ объявление",
        help_text="Выделяется в поиске и получает приоритет"
    )

    def __str__(self):
        return self.title
    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites',)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favorited_by', )
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        unique_together = ('user', 'ad')


class Banner(models.Model):
    title = models.CharField(max_length=100,)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Review(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   # ← важно для редактирования

    class Meta:
        unique_together = ('ad', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.ad.title} ({self.rating}★)"

    # Метод для проверки права на редактирование
    def can_edit(self, current_user):
        return self.user == current_user
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Телефон"
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name="Аватарка"
    )
    bio = models.TextField(blank=True, null=True, verbose_name="О себе")

    def __str__(self):
        return f"Профиль {self.user.username}"