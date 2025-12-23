import django_filters
from .models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(
        method="filter_is_active", label="Is Active"
    )

    class Meta:
        model = Borrowing
        fields = ["status", "user", "book"]

    def filter_is_active(self, queryset, name, value):
        if value is True:
            return queryset.filter(actual_return_date__isnull=True)
        elif value is False:
            return queryset.filter(actual_return_date__isnull=False)
        return queryset
