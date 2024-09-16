from django.urls import path, include
from rest_framework_simplejwt import views
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    SignupView,
    SigninView,
    SignoutView,
    EmailTokenObtainPairView,
    ProtectedView,
    UserViewSet
)


router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('signout/', SignoutView.as_view(), name='signout'),

    path(
        'token/',
        views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),  # by username
    path(
        'token/refresh/',
        views.TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'token/',
        EmailTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),  # by e-mail

    path('protected/', ProtectedView.as_view(), name='protected'),

    path('', include(router.urls)),
]
