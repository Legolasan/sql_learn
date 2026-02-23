import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

    # Google Analytics - set GA_TRACKING_ID environment variable to enable
    app.config['GA_TRACKING_ID'] = os.environ.get('GA_TRACKING_ID', '')

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.concepts import concepts_bp
    from app.routes.playground import playground_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(concepts_bp, url_prefix='/concept')
    app.register_blueprint(playground_bp, url_prefix='/playground')

    # Make concepts available in all templates
    from app.concepts import get_all_concepts

    @app.context_processor
    def inject_concepts():
        return {
            'all_concepts': get_all_concepts(),
            'ga_tracking_id': app.config.get('GA_TRACKING_ID', ''),
        }

    return app
