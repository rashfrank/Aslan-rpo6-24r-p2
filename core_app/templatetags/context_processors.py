from core_app.models import Banner

def active_banners(request):
    banners = Banner.objects.filter(is_active=True).order_by('?')  # ? = случайный порядок
    return {'banners': banners}