from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.static import serve
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework_jwt.views import obtain_jwt_token
from drf_network_pipeline.api.user import UserViewSet

import drf_network_pipeline.api.ml as ml_api
import drf_network_pipeline.index


schema_view = get_swagger_view(title="DRF Swagger with JWT")


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"mlprepare", ml_api.MLPrepareViewSet)
router.register(r"ml", ml_api.MLJobViewSet)
router.register(r"mlresults", ml_api.MLJobResultViewSet)


urlpatterns = [
    path("admin/",
         admin.site.urls,
         name="admin"),
    path("api-auth/",
         include("rest_framework.urls")),
    path("api-token-auth/",
         obtain_jwt_token),
    path("swagger/",
         schema_view),
    path("",
         include(router.urls)),
    path("accounts/",
         include("rest_registration.api.urls"),
         name="account-create"),
]

if settings.DEBUG:
    import debug_toolbar  # noqa
    urlpatterns = [
        path("__debug__/",
             include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.INCLUDE_DOCS:
    # could also make the user login required:
    # noqa https://stackoverflow.com/questions/20386445/integrating-sphinx-and-django-in-order-to-require-users-to-log-in-to-see-the-doc
    urlpatterns = [
        path(
            'docs/',
            drf_network_pipeline.index.handle_sphinx_doc_index,
            name="sphinx_doc_index"),
        re_path(
            r'^docs/(?P<path>.*)',
            serve,
            {
                'document_root': settings.DOCS_ROOT
            },
            name="sphinx_all_docs"),
    ] + urlpatterns
