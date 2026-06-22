"""User model.

Renamed from ``models/database/db_usuario.py`` (class ``Usuario``) to a
single, English, PEP 8-styled module -- ``models/user.py`` / class
``User`` -- following the convention used by virtually every Flask
tutorial and the Flask-Login documentation itself.

Two redundancies from the previous version were removed here:

1. The custom ``__init__`` only copied each argument onto ``self`` with the
   same name; SQLAlchemy's declarative base already provides exactly that
   behaviour via keyword arguments, so the override added no value.
2. Password hashing/verification was duplicated in every route that needed
   it. It now lives once, on the model, via ``set_password`` /
   ``check_password``.
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """A registered user of the application."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    def set_password(self, raw_password: str) -> None:
        """Hash and store ``raw_password``. Never store plain text."""
        self.password_hash = generate_password_hash(raw_password, method="scrypt")

    def check_password(self, raw_password: str) -> bool:
        """Return True if ``raw_password`` matches the stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper only
        return f"<User id={self.id} email={self.email!r}>"
