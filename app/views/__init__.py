import datetime
import json

from aiohttp import web, hdrs
from marshmallow import Schema

from app.exceptions import APIException, BaseAPIException, NotFound, AuthError
from app.serializers import ModelSerializer


class BaseView(web.View):
    serializer = Schema()
    response_serializer = Schema()
    permission_classes = ()
    user = None

    def check_permissions(self):
        for permission in self.permission_classes:
            if not permission().has_permission(self.request):
                raise AuthError()

    async def pre_process_request(self):
        self.user = await self.get_user()
        self.request.user = self.user
        self.check_permissions()
        if self.request._method in {hdrs.METH_POST, hdrs.METH_PUT, hdrs.METH_PATCH, hdrs.METH_DELETE}:
            data_raw = await self.request.text()
            if data_raw:
                data = json.loads(data_raw)
            else:
                data = {}
        else:
            data = self.request.query
        result = self.serializer.load(data)
        if result.errors:
            raise APIException(
                details={
                    'fieldErrors': result.errors,
                    'details': 'Validation failed'
                },
                status_code=400
            )
        self.validated_data = result.data

    async def get_user(self):
        token = self.request.headers.get('Authorization')
        if not token:
            return
        user = await User.filter(token=token).first()
        return user

    async def _iter(self):
        if self.request.method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request.method.lower(), None)
        if method is None:
            self._raise_allowed_methods()
        try:
            await self.pre_process_request()
            resp = await method()
        except BaseAPIException as e:
            resp = e.response
        return resp

    def get_request_url(self, params):
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = 'true' if value else 'false'
            elif isinstance(value, datetime.datetime):
                params[key] = value.isoformat()
        uri = self.request.match_info.route.resource.url_for().with_query(params)
        return f'{self.request.scheme}://{self.request.host}{uri}'


class ViewSet(BaseView):
    serializers_map = {}
    default_serializer = Schema()
    default_response_serializer = Schema()
    response_serializer_map = {}

    @property
    def serializer(self):
        serializer = self.serializers_map.get(self.request.method, self.default_serializer)
        return serializer

    @property
    def response_serializer(self):
        serializer = self.response_serializer_map.get(self.request.method, self.default_response_serializer)
        return serializer


class GenericViewSet(ViewSet):
    queryset = None

    def get_queryset(self):
        return self.queryset.all()

    async def get_object(self):
        queryset = self.get_queryset()
        instance_id = self.request.match_info.get('id')
        if not instance_id:
            raise NotFound()
        instance = await queryset.filter(id=instance_id).first()
        if not instance:
            raise NotFound()
        return instance


class ListMixin:
    pagination_class = None
    ordering = None

    def paginate_query(self, queryset):
        return self.pagination_class().paginate_query(queryset, self.request)

    def paginate_result(self, result, count):
        return self.pagination_class().paginate_result(result, count, self.request)

    def order_queryset(self, queryset):
        ordering = self.request.query.get('order_by', self.ordering)
        if not ordering:
            return queryset
        try:
            queryset = queryset.order_by(ordering)
        except AssertionError:
            pass
        return queryset

    async def get(self):
        queryset = self.get_queryset()
        if self.pagination_class:
            queryset = self.paginate_query(queryset)
        queryset = self.order_queryset(queryset)
        instance_list = await queryset.filter(**self.validated_data)
        instance_count = await self.get_queryset().filter(**self.validated_data).count()
        if isinstance(self.response_serializer, ModelSerializer):
            response_data = await self.response_serializer.dump_with_prefetch(instance_list)
        else:
            response_data, _ = self.response_serializer.dump(instance_list)
        if self.pagination_class:
            response_data = self.paginate_result(response_data, instance_count)
        return web.json_response(response_data)


class CreateMixin:
    async def post(self):
        instance = await self.queryset.model.create(**self.validated_data)
        if isinstance(self.response_serializer, ModelSerializer):
            response_data = await self.response_serializer.dump_with_prefetch(instance)
        else:
            response_data, _ = self.response_serializer.dump(instance)
        return web.json_response(response_data)


class RetrieveMixin:
    async def get(self):
        instance = await self.get_object()
        if isinstance(self.response_serializer, ModelSerializer):
            response_data = await self.response_serializer.dump_with_prefetch(instance)
        else:
            response_data, _ = self.response_serializer.dump(instance)
        return web.json_response(response_data)


class UpdateMixin:
    async def patch(self):
        instance = await self.get_object()
        for field, value in self.validated_data.items():
            setattr(instance, field, value)
        await instance.save()
        if isinstance(self.response_serializer, ModelSerializer):
            response_data = await self.response_serializer.dump_with_prefetch(instance)
        else:
            response_data, _ = self.response_serializer.dump(instance)
        return web.json_response(response_data)


class DestroyMixin:
    async def delete(self):
        instance = await self.get_object()
        await instance.delete()
        return web.json_response(status=204)


class GenericListViewSet(ListMixin, CreateMixin, GenericViewSet):
    pass


class GenericDetailViewSet(RetrieveMixin, UpdateMixin, DestroyMixin, GenericViewSet):
    pass
