from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin):
    pass
