from django.contrib import admin

from apps.listings.models import Listing, ViewHistory, SearchHistory


@admin.register(Listing)
class ListingModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ViewHistory)
class ViewHistoryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SearchHistory)
class LSearchHistoryModelAdmin(admin.ModelAdmin):
    pass
