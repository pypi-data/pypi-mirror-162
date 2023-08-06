import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
from django.utils.encoding import force_str as force_text
from django.utils.functional import Promise
from django.views.generic.base import TemplateView

logger = logging.getLogger(__name__)


class LazyEncoder(DjangoJSONEncoder):
    """Encodes django's lazy i18n strings
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONResponseView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(context,
                                content_type='application/json',
                                **response_kwargs)
        add_never_cache_headers(response)
        return response

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        func_val = self.get_context_data(**kwargs)
        assert isinstance(func_val, dict)
        response = dict(func_val)

        dump = json.dumps(response, cls=LazyEncoder)
        return self.render_to_response(dump)
