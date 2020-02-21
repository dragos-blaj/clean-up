from sqlalchemy.orm import relationship

from cleanup.database import db
from cleanup.cleaner.models.cleaners_cities import cleaners_cities


class Cleaner(db.Model):
    __tablename__ = 'cleaners'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)

    cities = relationship('City',
                          secondary=cleaners_cities,
                          back_populates='cleaners')

