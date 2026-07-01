# Archivo principal de rutas del proyecto Django:
# conecta el panel de administración, las rutas de la app core y permite servir archivos media en desarrollo.

from django.contrib import admin
from django.urls import path, include

# 🔥 IMPORTANTE PARA SERVIR IMÁGENES
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # 👈 tus urls de la app core
]

# 🔥 ESTA PARTE PERMITE SERVIR LOS ARCHIVOS MEDIA (AVATARES)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)