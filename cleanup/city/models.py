from sqlalchemy.orm import relationship

from cleanup.database import db
from cleanup.cleaner.models.cleaners_cities import cleaners_cities


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    zipcode = db.Column(db.String, nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )

    cleaners = relationship('Cleaner',
                            secondary=cleaners_cities,
                            back_populates='cities')
