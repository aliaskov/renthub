from django.urls import path, include


urlpatterns = [
    path('users/', include('apps.users.urls')),
    path('listings/', include('apps.listings.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('reviews/', include('apps.reviews.urls')),
]
