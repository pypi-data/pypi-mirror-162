from flask import Flask


def create_server(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkfgdfjn344_!67#'

    from pyjano.server.jana import jana_blueprint
    app.register_blueprint(jana_blueprint)
    return app

