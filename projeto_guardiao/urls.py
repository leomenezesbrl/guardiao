from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('guardiao.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.http import JsonResponse

def debug_view(request):
    import os
    import django
    from django.db import connection

    data = {
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE'),
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'DEBUG': os.environ.get('DEBUG'),
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'DB_CONNECTION_TEST': False,
    }
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        data['DB_CONNECTION_TEST'] = True
    except Exception as e:
        data['DB_CONNECTION_ERROR'] = str(e)

    return JsonResponse(data)

urlpatterns += [
    path('debug/', debug_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)