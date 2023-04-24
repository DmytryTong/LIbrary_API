import django_filters

from borrowing.models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name="user__id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Borrowing
        fields = ["user_id", "is_active"]
