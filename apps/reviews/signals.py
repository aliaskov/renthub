from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.reviews.models import Review


@receiver(post_save, sender=Review)
def update_listing_rating_on_save(sender, instance, created, **kwargs):
    if created:
        instance.listing.update_rating()


@receiver(post_delete, sender=Review)
def update_listing_rating_on_delete(sender, instance, **kwargs):
    instance.listing.update_rating()
