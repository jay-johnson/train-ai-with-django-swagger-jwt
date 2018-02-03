from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework_jwt.views import obtain_jwt_token
from drf_network_pipeline.api.user import UserViewSet

import drf_network_pipeline.api.ml as ml_api


schema_view = get_swagger_view(title="DRF Swagger with JWT")


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)


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
    path("mlprepare/",
         ml_api.MLPrepareViewSet.as_view({
             "post": "create"
         }),
         name="mlpreparecreate"),
    path("ml/run/",
         ml_api.MLJobViewSet.as_view({
             "post": "create"
         }),
         name="mljobcreate"),
    path("ml/<pk>/",
         ml_api.MLJobViewSet.as_view({
             "get": "get",
             "put": "update",
             "delete": "delete"
         }),
         name="mljobgpd"),
    path("mlresults/<pk>/",
         ml_api.MLJobResultViewSet.as_view({
             "get": "get",
             "put": "update",
             "delete": "delete"
         }),
         name="mljobresults"),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
