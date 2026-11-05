from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GiftViewSet, TagViewSet, FileViewSet

router = DefaultRouter()
router.register(r'gifts', GiftViewSet, basename='gift')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('', include(router.urls)),
]
