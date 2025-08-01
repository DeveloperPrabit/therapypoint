from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # ✅ Your main app URLs
    path("", include("myapp.urls")),

    # ✅ CKEditor URLs (required for rich text editor)
    # path("ckeditor/", include("ckeditor_uploader.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
