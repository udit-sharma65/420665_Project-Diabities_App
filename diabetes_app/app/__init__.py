from flask import Flask, render_template

from config import Config

from .extensions import csrf, db, login_manager
from .services.predictor import SMOKING_LABELS, get_model


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .auth import bp as auth_bp
    from .main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.template_filter("datefmt")
    def datefmt(value):
        return value.strftime("%d %b %Y, %H:%M") + " UTC"

    @app.template_filter("smoking_label")
    def smoking_label(value):
        return SMOKING_LABELS.get(value, value)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    get_model()

    return app
