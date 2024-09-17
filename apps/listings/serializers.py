from django.urls import reverse
from rest_framework import serializers

from apps.users.serializers import UserSerializer
from apps.listings.models import Listing, ViewHistory, SearchHistory


class ChoicesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    def to_representation(self, instance):
        return {
            'id': instance[0],
            'name': instance[1]
        }


class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    is_user_owner = serializers.SerializerMethodField()
    property_type_display = serializers.SerializerMethodField()
    listing_url = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at',
            'rating',
            'number_of_reviews',
            'number_of_views'
        ]

    def get_is_user_owner(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return obj.owner == request.user
        return False

    def get_property_type_display(self, obj):
        return obj.get_property_type_display()

    def get_listing_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('listing-detail', kwargs={'pk': obj.pk})
            )
        return None


class ViewHistorySerializer(serializers.ModelSerializer):
    listing_str = serializers.SerializerMethodField()
    listing_url = serializers.SerializerMethodField()

    class Meta:
        model = ViewHistory
        exclude = ['id', 'user']

    def get_listing_str(self, obj):
        return f'{obj.listing.title} - {obj.listing.address}'

    def get_listing_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('listing-detail', kwargs={'pk': obj.listing.pk})
            )
        return None


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        exclude = ['id', 'user']
