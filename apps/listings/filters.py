from rest_framework import filters
from django.db.models import Q

from apps.listings.models import SearchHistory


class CustomSearchFilter(filters.SearchFilter):
    '''
    Проверяем icontains каждого слова отдельно, что-то вроде:
    WHERE field LIKE '%term%' OR field LIKE '%term%' OR ...
    '''
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        if search_terms:
            SearchHistory.objects.create(
                user=request.user,
                term=' '.join(search_terms)
            )
            if search_fields:
                query = Q()
                for term in search_terms:
                    term_query = Q()
                    for field in search_fields:
                        term_query |= Q(**{f"{field}__icontains": term})
                    query |= term_query
                return queryset.filter(query)
        return super().filter_queryset(request, queryset, view)
