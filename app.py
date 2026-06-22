
import os

import click
from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL, make_url

from config import CONFIG_BY_NAME
from controllers import routes
from extensions import db, login_manager
from models.user import User


def _ensure_mysql_database_exists(database_uri: str) -> None:

    url = make_url(database_uri)
    target_db_name = url.database
    server_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
    )

    server_engine = create_engine(server_url)
    try:
        with server_engine.connect() as connection:
            connection.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{target_db_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
        click.echo(f'Banco de dados MySQL "{target_db_name}" pronto.')
    finally:
        server_engine.dispose()


def create_app(config_name: str = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    config_class = CONFIG_BY_NAME.get(config_name, CONFIG_BY_NAME["development"])

    app = Flask(__name__, template_folder="views")
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    routes.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command("init-db")
    def init_db():
        _ensure_mysql_database_exists(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            db.create_all()
        click.echo("Tabelas criadas com sucesso.")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
