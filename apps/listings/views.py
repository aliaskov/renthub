from datetime import timedelta
from rest_framework import generics, viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from apps.listings.permissions import IsOwnerOrReadOnly
from apps.listings.models import (
    PropertyType,
    Listing,
    ViewHistory,
    SearchHistory
)
from apps.listings.serializers import (
    ChoicesSerializer,
    ListingSerializer,
    ViewHistorySerializer,
    SearchHistorySerializer
)
from apps.listings.filters import CustomSearchFilter
from apps.bookings.models import BookingStatus, Booking
from apps.reviews.serializers import ReviewSerializer


class PropertyTypeListView(generics.ListAPIView):
    queryset = PropertyType.choices
    serializer_class = ChoicesSerializer
    pagination_class = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['results_label'] = 'results'
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            self.get_serializer_context()['results_label']: response.data
        }
        return response


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        # filters.SearchFilter,
        CustomSearchFilter,
        filters.OrderingFilter
    ]
    # https://docs.djangoproject.com/en/5.1/ref/models/querysets/#field-lookups
    filterset_fields = {
        # Цена (возможность указать минимальную и максимальную цену)
        'price': ['lte', 'gte'],
        # Количество комнат (возможность указать диапазон количества комнат)
        'rooms': ['range'],
        # Тип жилья (возможность выбрать тип жилья квартира,
        # дом, студия и т.д.)
        'property_type': ['exact'],
        # Местоположение: (возможность указать город или район в Германии)
        'address': ['icontains']
    }
    # Пользователь вводит ключевые слова, по которым производится поиск
    # в заголовках и описаниях объявлений
    search_fields = ['title', 'description']
    # Возможность сортировки по цене (возрастание/убывание),
    # дате добавления (новые/старые)
    ordering_fields = [
        'price',
        'created_at',
        'rating',
        'number_of_reviews',
        'number_of_views'
    ]
    ordering = ['id']

    def get_queryset(self):
        if self.action == 'list':
            return Listing.objects.filter(is_active=True)
        return Listing.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        else:
            return [IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Запрет на просмотр неактивных объявлений, если это не владелец
        if not instance.is_active and instance.owner != request.user:
            raise PermissionDenied()
        # Если это не владелец, записываем просмотр
        if request.user.is_authenticated and instance.owner != request.user:
            ViewHistory.objects.update_or_create(
                listing=instance,
                user=request.user
            )
            instance.update_views()
        return super().retrieve(request, *args, **kwargs)

    @action(
        methods=['get'],
        detail=False,
        url_path='my-created',
        permission_classes=[permissions.IsAuthenticated]
    )
    def my_created(self, request):
        queryset = Listing.objects.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False,
        url_path='my-view-history',
        permission_classes=[permissions.IsAuthenticated]
    )
    def my_view_history(self, request):
        view_history = ViewHistory.objects.filter(
            user=request.user
        ).order_by('-viewed_at')
        view_history = [view for view in view_history]
        serializer = ViewHistorySerializer(
            view_history, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False,
        url_path='my-search-history',
        permission_classes=[permissions.IsAuthenticated]
    )
    def my_search_history(self, request):
        search_history = SearchHistory.objects.filter(
            user=request.user
        ).order_by('-searched_at')
        search_history = [search for search in search_history]
        serializer = SearchHistorySerializer(search_history, many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False,
        url_path='property-types',
        permission_classes=[permissions.AllowAny]
    )
    def property_types(self, request):
        queryset = PropertyType.choices
        serializer = ChoicesSerializer(queryset, many=True)
        return Response({'results': serializer.data})

    @action(
        methods=['get'],
        detail=True,
        url_path='reserved-periods',
        permission_classes=[permissions.AllowAny]
    )
    def reserved_periods(self, request, pk=None):
        listing = self.get_object()
        bookings = Booking.objects.filter(
            listing=listing,
            status=BookingStatus.CONFIRMED
        ).values('check_in_date', 'check_out_date')
        reserved_dates = [
            {
                'check_in': booking['check_in_date'],
                'check_out': booking['check_out_date']
            }
            for booking in bookings
        ]
        return Response(reserved_dates)

    @action(
        methods=['get'],
        detail=True,
        url_path='reserved-dates',
        permission_classes=[permissions.AllowAny]
    )
    def reserved_dates(self, request, pk=None):
        listing = self.get_object()
        bookings = Booking.objects.filter(
            listing=listing,
            status=BookingStatus.CONFIRMED
        ).values('check_in_date', 'check_out_date')
        reserved_dates = set()
        for booking in bookings:
            check_in_date = booking['check_in_date']
            check_out_date = booking['check_out_date']
            current_date = check_in_date
            while current_date <= check_out_date:
                reserved_dates.add(current_date)
                current_date += timedelta(days=1)
        reserved_dates = sorted(list(reserved_dates))
        return Response(reserved_dates)

    @action(
        methods=['get'],
        detail=True,
        url_path='reviews',
        permission_classes=[permissions.AllowAny]
    )
    def reviews(self, request, pk=None):
        listing = self.get_object()
        reviews = listing.reviews.all()
        serializer = ReviewSerializer(
            reviews, many=True, context={'request': request}
        )
        return Response(serializer.data)
