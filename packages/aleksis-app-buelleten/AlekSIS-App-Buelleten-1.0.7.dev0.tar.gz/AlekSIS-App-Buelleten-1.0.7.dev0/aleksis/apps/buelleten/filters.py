from django_filters import FilterSet

from .models.base import Display


class DisplaysFilter(FilterSet):
    class Meta:
        model = Display
        fields = ["hostname"]
