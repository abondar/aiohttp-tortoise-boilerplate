# aiohttp-tortoise-boilerplate
Boilerplate service built using [aiohttp](https://github.com/aio-libs/aiohttp) and [tortoise ORM](https://github.com/Zeliboba5/tortoise-orm).

## What that boilerplate is about?

Altogether this boilerplate aims to provide [drf](https://github.com/encode/django-rest-framework/)-like
experience, while working with asyncio code.

Core of this boilerplate is `views/__init__.py` file, that provides
generic views usable for building restful API.

Your views should inherit from views.BaseView or it's descendants.
You can write your serializers in `serializers.py`, and define them as
request and response serializers for views.

To validate incoming data you should define serializer for it,
and pass it to your view, than your data
will be available in ```self.validated_data``` in your view,
and all validation errors will be automatically sent to client.

Regarding response serializers you can use `ModelSerializer` for your
model instances, which allows serializer determine which relations
should be prefetched for given instance.
