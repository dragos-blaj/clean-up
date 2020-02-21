import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from cleanup.auth.models import User
from cleanup.database import db


@click.command("add-user")
@click.argument('username')
@click.argument('password')
@with_appcontext
def add_user_command(username, password):
    hashed_password = generate_password_hash(password)
    db.session.add(User(username=username, _password=hashed_password))
    db.session.commit()
    click.echo("Added user.")
