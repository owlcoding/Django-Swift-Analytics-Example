from rest_framework import routers

from django.conf.urls import url, include

from .apis import LogEventViewSet, ClientViewSet

router = routers.DefaultRouter()
router.register(r'events', LogEventViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
