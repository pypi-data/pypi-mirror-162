# -*- coding: utf-8 -*-
import logging
from math import ceil

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.utils.html import escape, format_html

from .mixins import JSONResponseView

logger = logging.getLogger(__name__)


class BaseKTDatatableView(JSONResponseView):
    model = None
    columns = []
    _columns = []  # internal cache for columns definition
    none_string = ''
    escape_values = True  # if set to true then values returned by render_column will be escaped
    columns_data = []

    FILTER_ISTARTSWITH = 'istartswith'
    FILTER_ICONTAINS = 'icontains'

    @property
    def _query_dict(self):
        if self.request.method == 'POST':
            return self.request.POST
        else:
            return self.request.GET

    def get_filter_method(self):
        """ Returns preferred filter method """
        return self.FILTER_ICONTAINS

    def initialize(self, *args, **kwargs):
        pass

    def get_columns(self):
        return [column['field'] for column in self.columns]

    @staticmethod
    def _column_value(obj, key):
        """ Returns the value from a queryset item
        """
        if isinstance(obj, dict):
            return obj.get(key, None)

        return getattr(obj, key, None)

    def _render_column(self, row, column):
        """ Renders a column on a row. column can be given in a module notation eg. document.invoice.type
        """
        # try to find rightmost object
        obj = row
        parts = column.split('.')
        for part in parts[:-1]:
            if obj is None:
                break
            obj = getattr(obj, part)

        # try using get_OBJECT_display for choice fields
        if hasattr(obj, 'get_%s_display' % parts[-1]):
            value = getattr(obj, 'get_%s_display' % parts[-1])()
        else:
            value = self._column_value(obj, parts[-1])

        if value is None:
            value = self.none_string

        if self.escape_values:
            value = escape(value)

        return value

    def render_column(self, row, column):
        """ Renders a column on a row. column can be given in a module notation eg. document.invoice.type
        """
        value = self._render_column(row, column)
        if value and hasattr(row, 'get_absolute_url'):
            return format_html('<a href="{}">{}</a>', row.get_absolute_url(), value)
        return value

    def ordering(self, qs):
        sort_field = self._query_dict.get('sort[field]')
        if sort_field:
            if self._query_dict.get('sort[sort]') == "desc":
                sort_field = f'-{sort_field}'
            return qs.order_by(sort_field)

        return qs

    def paging(self, qs):
        page = int(self._query_dict.get('pagination[page]'))
        per_page = int(self._query_dict.get('pagination[perpage]'))

        if page > 0:
            start = (page - 1) * per_page
            limit = page * per_page

            return qs[start:limit]
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all()

    def get_model(self):
        if self.model:
            return self.model
        return self.get_initial_queryset().model

    def filter_queryset(self, qs):
        q = Q()
        search = self._query_dict.get('query[generalSearch]')
        filter_method = self.get_filter_method()

        for column in self._columns:
            column_search = self._query_dict.get(f'query[{column}]')
            try:
                self.get_model()._meta.get_field(column)
                if column_search:
                    q |= Q(**{f'{column}__{filter_method}': column_search})
                if search:
                    q |= Q(**{f'{column}__{filter_method}': search})
            except FieldDoesNotExist:
                pass
        qs = qs.filter(q)
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({column: self.render_column(item, column) for column in self._columns})

        return data

    def get_context_data(self, *args, **kwargs):
        try:
            self.initialize()

            self._columns = self.get_columns()

            # prepare initial queryset
            qs = self.get_initial_queryset()

            # apply filters
            qs = self.filter_queryset(qs)

            # store the total number of records
            total_records = qs.count()

            # apply ordering
            qs = self.ordering(qs)

            # apply pagintion
            qs = self.paging(qs)

            data = self.prepare_results(qs)
            meta = {'page': self._query_dict.get('pagination[page]'),
                    'pages': ceil(total_records / int(self._query_dict.get('pagination[perpage]'))),
                    'perpage': self._query_dict.get('pagination[perpage]'),
                    'total': total_records,
                    'sort': self._query_dict.get("sort[sort]"),
                    'field': self._query_dict.get("sort[field]")}

            return {'meta': meta, 'data': data}
        except Exception as e:
            logger.exception(str(e))
            raise e
