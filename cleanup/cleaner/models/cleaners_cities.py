from cleanup.database import db

# Association table for cleaners and cities
cleaners_cities = db.Table(
    'cleaners_cities',
    db.Column('cleaner_id', db.ForeignKey('cleaners.id'), primary_key=True),
    db.Column('city_id', db.ForeignKey('cities.id'), primary_key=True)
)