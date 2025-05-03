from core.views import HealthCheckView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .env import env

admin.autodiscover()

ADMIN_PATH = env("DJANGO_ADMIN_PATH", default="admin/")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path(ADMIN_PATH + "docs/", include(admindocs_urls)),
    path(ADMIN_PATH, admin.site.urls),
    path("", include("order.urls", namespace="orders")),
    # ==============================================|
    # ============ 3rd party apps URLs =============|
    # ==============================================|
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DJANGO_ENV in ["DEV", "TEST"]:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# admin site display
admin.site.site_header = "Ayora Admin"
admin.site.site_title = "Ayora Admin Portal"
admin.site.index_title = "Welcome to Ayora"
admin.site.site_url = settings.CLIENT_URL
# admin site actions
admin.site.disable_action("delete_selected")
