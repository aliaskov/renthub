from django.urls import reverse
from rest_framework import serializers

from apps.reviews.models import Review
from apps.bookings.models import BookingStatus, Booking
from apps.users.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError(
                'The rating must be from 1 to 5.'
            )
        return value

    def validate(self, data):
        request = self.context.get('request')
        listing = data.get('listing')
        user = request.user
        if not listing.is_active:
            raise serializers.ValidationError(
                'You cannot leave a review for inactive listing.'
            )
        # Проверяем, существует ли уже отзыв от этого пользователя
        # на это объявление
        existing_review = Review.objects.filter(
            user=user, listing=listing
        ).exists()
        if existing_review:
            raise serializers.ValidationError(
                'You have already left a review for this listing.'
            )
        if listing.owner == user:
            raise serializers.ValidationError(
                'You cannot leave a review for your listing.'
            )
        # Проверка, что у пользователя есть подтвержденное
        # бронирование для этого объявления
        has_booking = Booking.objects.filter(
            listing=listing,
            user=user,
            status=BookingStatus.CONFIRMED
        ).exists()
        if not has_booking:
            raise serializers.ValidationError(
                'You can only leave a review if you have a confirmed booking.'
            )
        return data

    def get_listing_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('listing-detail', kwargs={'pk': obj.pk})
            )
        return None
