from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User

from apps.listings.models import Listing


class BookingStatus(models.IntegerChoices):
    PENDING = 0, _('Pending')
    CONFIRMED = 1, _('Confirmed')
    REJECTED = 2, _('Rejected')
    CANCELLED = 3, _('Cancelled')


class Booking(models.Model):
    listing = models.ForeignKey(
        to=Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    status = models.IntegerField(
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} booked {self.listing}'

    def confirm(self, user):
        '''Подтверждение бронирования владельцем жилья.'''
        if user != self.listing.owner:
            raise PermissionError('Only the host can confirm the booking.')
        if self.status != BookingStatus.PENDING:
            raise ValueError('Only pending bookings can be confirmed.')
        self.status = BookingStatus.CONFIRMED
        self.save()

    def reject(self, user):
        '''Отклонение бронирования владельцем жилья.'''
        if user != self.listing.owner:
            raise PermissionError('Only the owner can reject the booking.')
        if self.status != BookingStatus.PENDING:
            raise ValueError('Only pending bookings can be rejected.')
        self.status = BookingStatus.REJECTED
        self.save()

    def cancel(self, user):
        '''Отмена бронирования арендатором.'''
        if user != self.user:
            raise PermissionError('Only the renter can cancel the booking.')
        if self.status != BookingStatus.CONFIRMED:
            raise ValueError('Only confirmed bookings can be cancelled.')
        if not self.is_cancelable():
            raise ValueError('It\'s too late to cancel this booking.')
        self.status = BookingStatus.CANCELLED
        self.save()

    def is_cancelable(self):
        '''Может ли арендатор отменить бронирование?'''
        days_to_check_in_date = (
            self.check_in_date - timezone.now().date()
        ).days
        return days_to_check_in_date >= 1
