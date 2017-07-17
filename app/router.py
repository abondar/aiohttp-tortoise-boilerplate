from app import views


def setup_routes(app):
    app.router.add_route('*', '/', views.IndexView, name='index')
