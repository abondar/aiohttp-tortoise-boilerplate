from marshmallow import Schema, fields, ValidationError, validates, validates_schema, post_load


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
