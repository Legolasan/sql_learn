from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.concepts import concepts_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(concepts_bp, url_prefix='/concept')

    # Make concepts available in all templates
    from app.concepts import get_all_concepts

    @app.context_processor
    def inject_concepts():
        return {'all_concepts': get_all_concepts()}

    return app
