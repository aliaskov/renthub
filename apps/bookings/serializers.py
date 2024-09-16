from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers

from apps.users.serializers import UserSerializer
from apps.bookings.models import BookingStatus, Booking


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    booking_url = serializers.SerializerMethodField()
    listing_url = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

        read_only_fields = [
            'user', 'price', 'status', 'created_at', 'updated_at'
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_booking_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('booking-detail', kwargs={'pk': obj.pk})
            )
        return None

    def get_listing_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('listing-detail', kwargs={'pk': obj.listing.pk})
            )
        return None

    def validate(self, data):
        listing = data.get('listing')
        if not listing.is_active:
            raise serializers.ValidationError(
                'It is not possible to book an inactive listing.'
            )
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        if check_in_date < timezone.now().date():
            raise serializers.ValidationError(
                'The booking start date cannot be in the past.'
            )
        if check_in_date >= check_out_date:
            raise serializers.ValidationError(
                'The start date of the booking must be before the end date.'
            )
        overlapping_bookings = Booking.objects.filter(
            listing=listing,
            status=BookingStatus.CONFIRMED
        ).filter(
            Q(check_in_date__lt=check_out_date)
            & Q(check_out_date__gt=check_in_date)
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError(
                'The selected dates overlap with existing bookings.'
            )
        return data
