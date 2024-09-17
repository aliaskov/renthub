from django.contrib import admin

from apps.bookings.models import Booking


@admin.register(Booking)
class BookingModelAdmin(admin.ModelAdmin):
    pass
