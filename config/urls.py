from .yasg import yasg_urlpatterns
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('api/accounts/', include('account.urls')),
    path('api/blog/', include('blog.urls', namespace='blog')),
    path('admin/', admin.site.urls),
]

urlpatterns += yasg_urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
