from marshmallow import Schema, fields, ValidationError, validates, validates_schema, post_load

from app.exceptions import APIException


class PaginatedRequestSerializer(Schema):
    page = fields.Integer(missing=1)
    page_size = fields.Integer(missing=10)

    @post_load
    def parse_page_params(self, data):
        page_size = data.pop('page_size')
        page = data.pop('page')
        data['limit'] = page_size
        data['offset'] = (page - 1) * page_size
        return data


class ModelSerializer(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert issubclass(self.Meta.model, Model)
        self.model = self.Meta.model
        self.fields_to_prefetch = self._get_prefetch_fields()

    def _get_prefetch_fields(self):
        fields_to_prefetch = []
        for field_name, field in self.fields.items():
            if isinstance(field, fields.Nested):
                if issubclass(field.nested, ModelSerializer):
                    related_fields_to_prefetch = field.nested()._get_prefetch_fields()
                    if related_fields_to_prefetch:
                        fields_to_prefetch += [
                            '{}__{}'.format(field_name, f) for f in related_fields_to_prefetch
                        ]
                    else:
                        fields_to_prefetch.append(field_name)
        return fields_to_prefetch

    async def dump_with_prefetch(self, obj, many=None, *args, **kwargs):
        if many or self.many:
            await self.model.fetch_for_list(obj, *self.fields_to_prefetch)
        else:
            await obj.fetch_related(*self.fields_to_prefetch)
        result, errors = self.dump(obj, many, *args, **kwargs)
        if errors:
            raise APIException(
                details={
                    'fieldErrors': errors,
                    'details': 'Validation failed'
                },
                status_code=400
            )
        return result

    class Meta:
        model = None
