import datetime

from multidict import MultiDict


class PageNumberPagination:
    page_size = 10

    def paginate_query(self, queryset, request):
        query_params = MultiDict(request.query)
        try:
            page = int(query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = int(query_params.get('page_size', self.page_size))
        except (ValueError, TypeError):
            page_size = self.page_size

        offset = (page - 1) * page_size
        return queryset.limit(page_size).offset(offset)

    def paginate_result(self, result, count, request):
        query_params = MultiDict(request.query)
        try:
            page = int(query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = int(query_params.get('page_size', self.page_size))
        except (ValueError, TypeError):
            page_size = self.page_size

        response = {
            'count': count,
            'next': None,
            'previous': None,
            'result': result,
        }

        if page > 1:
            previous_page_params = query_params
            if (page_size * (page - 1)) > count and count:
                previous_page_params['page'] = int(count / page_size) + 1
            else:
                previous_page_params['page'] = page - 1
            response['previous'] = self.get_request_url(previous_page_params, request)

        if (page * page_size) < count:
            next_page_params = query_params
            next_page_params['page'] = page + 1
            response['next'] = self.get_request_url(next_page_params, request)

        return response

    def get_request_url(self, params, request):
        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = 'true' if value else 'false'
            elif isinstance(value, datetime.datetime):
                params[key] = value.isoformat()
        uri = request.match_info.route.resource.url_for().with_query(params)
        return f'{request.scheme}://{request.host}{uri}'
