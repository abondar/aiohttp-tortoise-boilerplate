from app import views
from app.doc_generator import DocumentationGenerator


def setup_routes(app):
    # app.router.add_route('*', '/', views.BaseView, name='base')

    app.router.add_route('*', '/api/docs/', DocumentationGenerator(app).docs_view)
