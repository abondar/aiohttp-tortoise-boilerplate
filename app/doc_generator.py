from aiohttp import web
from aiohttp.web_urldispatcher import PlainResource, DynamicResource
from marshmallow import fields as marshmallow_field

from app.serializers import TimeStamp, ModelSerializer
from app.views import ViewSet, BaseView, StandardPagination
import inspect


FIELD_TYPES_VERBOSE = {
    marshmallow_field.Boolean: 'Boolean',
    marshmallow_field.String: 'String',
    marshmallow_field.Integer: 'Integer',
    marshmallow_field.DateTime: 'Datetime',
    marshmallow_field.Nested: 'Nested entity',
    marshmallow_field.Float: 'Float',
    marshmallow_field.Decimal: 'Decimal',
    marshmallow_field.Date: 'ISO Date',
}


class DocumentationView(web.View):
    async def get(self):
        return web.json_response(self.request.app['_schema'])


class DocumentationGenerator:
    METHOD_FUNCTIONS = {'get', 'post', 'delete', 'put', 'patch'}

    def __init__(self, app):
        self.app = app
        self._generate_schema()

    def _get_method_parameters(self, serializer):
        parameters = []
        for field in serializer.fields.values():
            if field.dump_only:
                continue
            name = field.load_from if field.load_from else field.name
            parameter_info = {
                'name': name,
                'description': field.metadata.get('description', ''),
                'default': field.missing if field.missing else None,
                'required': field.required,
                'type': FIELD_TYPES_VERBOSE.get(field.__class__, 'Unknown type')
            }
            if isinstance(field, marshmallow_field.List):
                field_type = FIELD_TYPES_VERBOSE.get(field.container.__class__, "Unknown type")
                parameter_info['type'] = f'List of {field_type}'
            elif isinstance(field, marshmallow_field.Nested) and issubclass(field.nested, ModelSerializer):
                if field.many:
                    parameter_info['type'] = f'List of [{{{field.nested.Meta.model.__name__}}}]'
                else:
                    parameter_info['type'] = f'{{{field.nested.Meta.model.__name__}}}'
            parameters.append(parameter_info)
        return parameters

    def _get_response_fields(self, serializer):
        response_fields = []
        for field in serializer.fields.values():
            if field.load_only:
                continue
            name = field.dump_to if field.dump_to else field.name
            field_info = {
                'name': name,
                'description': field.metadata.get('description', ''),
                'type': FIELD_TYPES_VERBOSE.get(field.__class__, 'Unknown type')
            }

            if isinstance(field, marshmallow_field.List):
                field_type = FIELD_TYPES_VERBOSE.get(field.container.__class__, "Unknown type")
                field_info['type'] = f'List of [{field_type}]'
            elif isinstance(field, marshmallow_field.Nested) and issubclass(field.nested, ModelSerializer):
                if field.many:
                    field_info['type'] = f'List of [{{{field.nested.Meta.model.__name__}}}]'
                else:
                    field_info['type'] = f'{{{field.nested.Meta.model.__name__}}}'
            response_fields.append(field_info)
        return response_fields

    def _get_method_schema(self, handler, method_name, method):
        if issubclass(handler, ViewSet):
            request_serializer = handler.serializers_map.get(method_name.upper(), handler.default_serializer)
            response_serializer = handler.response_serializer_map \
                .get(method_name.upper(), handler.default_response_serializer)
        elif issubclass(handler, BaseView):
            request_serializer = handler.serializer
            response_serializer = handler.response_serializer
        else:
            return
        parameters = self._get_method_parameters(request_serializer)
        response_fields = self._get_response_fields(response_serializer)

        docstring = inspect.getdoc(method)

        method_schema = {
            'parameters': parameters,
            'response': {
                'is_list': response_serializer.many,
                'paginated': bool(hasattr(handler, 'pagination_class') and handler.pagination_class),
                'fields': response_fields,
            },
            'description': docstring if docstring else '',
        }
        return method_schema

    def _get_resource_schema(self, resource):
        if isinstance(resource, PlainResource):
            url_path = resource._path
        elif isinstance(resource, DynamicResource):
            url_path = resource._formatter
        else:
            return
        resource_schema = {
            'url': url_path,
        }
        handler = resource._routes[0].handler
        methods = inspect.getmembers(handler, predicate=inspect.iscoroutinefunction)
        for method_name, method in (m for m in methods if m[0] in self.METHOD_FUNCTIONS):
            method_schema = self._get_method_schema(handler, method_name, method)
            if not method_schema:
                continue
            resource_schema[method_name] = method_schema
        return resource_schema

    def _generate_schema(self):
        schema = {
            'paths': [],
            'info': {
                'title': 'API',
                'version': '1.0.0',
            },
        }
        for resource in self.app.router._resources:
            resource_schema = self._get_resource_schema(resource)
            if not resource_schema:
                continue
            schema['paths'].append(resource_schema)
        self.app['_schema'] = schema

    @property
    def docs_view(self):
        return DocumentationView
