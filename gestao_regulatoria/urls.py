# gestao_regulatoria/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe settings
from django.conf.urls.static import static # Importe static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Adicionado para servir arquivos estáticos e de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) # Usa o primeiro STATICFILES_DIRS
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Para arquivos de mídia