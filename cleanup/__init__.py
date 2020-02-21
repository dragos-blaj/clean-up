import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='postgres://local:GjK4gIkBcfxrznAu@localhost:20123/local_db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    print("instance path: {}".format(app.instance_path))
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from cleanup.auth.commands import add_user_command
    from cleanup.database import db, init_db_command

    db.init_app(app)

    from .auth.views import bp as auth_bp
    from .city.views import bp as city_bp
    from .cleaner.views import bp as cleaner_bp
    from .booking.views import bp as booking_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(cleaner_bp)
    app.register_blueprint(booking_bp)

    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)

    return app


