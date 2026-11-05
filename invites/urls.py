from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InviteViewSet

router = DefaultRouter()
router.register(r'invites', InviteViewSet, basename='invite')

urlpatterns = [
    path('', include(router.urls)),
]
