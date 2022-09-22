import django_filters.rest_framework as filter

from reviews.models import Title


class TitlesFilters(filter.FilterSet):
    """Фильтр для сортировки произведений по параметрам."""

    name = filter.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    category = filter.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    genre = filter.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    year = filter.NumberFilter(
        field_name='year',
        lookup_expr='icontains'
    )

    class Meta:
        fields = '__all__'
        model = Title
