from rest_framework import routers
from django.urls import path, include
from .views import JourneyViewSet, PrimaryExpenseViewSet, SecondaryExpenseViewSet

router = routers.DefaultRouter()
router.register(r'journey', JourneyViewSet)
router.register(r'primary-expense', PrimaryExpenseViewSet)
router.register(r'secondary-expense', SecondaryExpenseViewSet)


urlpatterns = [
    path('', include(router.urls)),
]