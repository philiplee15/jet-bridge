from sqlalchemy import inspect

from jet_bridge.filters import lookups
from jet_bridge.filters.filter import Filter
from jet_bridge.filters.filter_for_dbfield import FILTER_FOR_DBFIELD, FILTER_FOR_DBFIELD_DEFAULT


class FilterClass(object):
    filters = []

    def __init__(self, *args, **kwargs):
        self.meta = getattr(self, 'Meta', None)
        if 'context' in kwargs:
            self.request = kwargs['context'].get('request', None)
            self.handler = kwargs['context'].get('handler', None)
        self.update_filters()

    def update_filters(self):
        filters = []

        if self.meta:
            if hasattr(self.meta, 'model'):
                Model = self.meta.model
                mapper = inspect(Model)
                columns = mapper.columns

                if hasattr(self.meta, 'fields'):
                    columns = filter(lambda x: x.name in self.meta.fields, columns)

                for column in columns:
                    item = FILTER_FOR_DBFIELD.get(column.type, FILTER_FOR_DBFIELD_DEFAULT)
                    for lookup in [lookups.EXACT, lookups.ICONTAINS, lookups.IN]:
                        instance = item['filter_class'](field_name=column.key, model=Model, lookup=lookup)
                        filters.append(instance)

        declared_filters = filter(lambda x: isinstance(x[1], Filter), map(lambda x: (x, getattr(self, x)), dir(self)))

        for filter_name, filter_item in declared_filters:
            filter_item.name = filter_name
            filters.append(filter_item)

        self.filters = filters

    def filter_queryset(self, queryset):
        for item in self.filters:
            if self.handler and item.name:
                argument_name = '{}__{}'.format(item.name, item.lookup)
                value = self.handler.get_argument(argument_name, None)

                if value is None and item.lookup == lookups.DEFAULT_LOOKUP:
                    value = self.handler.get_argument(item.name, None)
            else:
                value = None

            queryset = item.filter(queryset, value)
        return queryset
