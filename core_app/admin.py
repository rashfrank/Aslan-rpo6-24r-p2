from django.contrib import admin
from .models import Category, City, Ad, Favorite,Banner
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
   list_display = ('name',)

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'city', 'price', 
                   'is_moderated', 'is_top', 'created_at')
    list_filter = ('is_moderated', 'is_top', 'category', 'city')
    list_editable = ('is_top', 'is_moderated')   # можно менять прямо в списке
    search_fields = ('title', 'description')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
 list_display = ('user', 'ad')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
  list_display = ('title', 'is_active', 'link')
