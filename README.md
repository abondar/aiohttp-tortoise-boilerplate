# aiohttp-boilerplate
Yet another boilerplate for aiohttp web service with PostgreSQL

To start the project use `docker-compose up -d`.
Don't forget to change password and db name in config and docker-compose.yml

You can write your database migrations by creating new file in migrations directory, they will be run
automatically on the start of the app.

Your views should inherit from views.BaseView
To validate incoming data you should define serializer for it, and pass it to your view, than your data
will be available in ```self.validated_data``` in your view, and all validation errors will be automatically
sent to client
