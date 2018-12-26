import sqlalchemy
from sqlalchemy import inspect, or_

from jet_bridge.filters.char_filter import CharFilter
from jet_bridge.filters.filter import EMPTY_VALUES
from jet_bridge.filters.filter_class import FilterClass


def filter_search_field(field):
    allowed_fields = [
        sqlalchemy.VARCHAR,
        sqlalchemy.TEXT,
        sqlalchemy.CHAR,
        sqlalchemy.JSON
    ]

    return isinstance(field.type, tuple(allowed_fields))


def get_model_search_filter(Model):
    mapper = inspect(Model)
    search_fields = list(map(lambda x: x, filter(filter_search_field, mapper.columns)))

    class SearchFilter(CharFilter):
        def filter(self, qs, value):
            value = self.clean_value(value)
            if value in EMPTY_VALUES:
                return qs

            operators = list(map(lambda x: x.ilike('%{}%'.format(value)), search_fields))
            return qs.filter(or_(*operators))

    return SearchFilter


def get_model_filter_class(Model):
    search_filter = get_model_search_filter(Model)

    class ModelFilterClass(FilterClass):
        _search = search_filter()

        class Meta:
            model = Model

    return ModelFilterClass
