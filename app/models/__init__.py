# Import all models here so Alembic can find them when generating migrations
from app.models.user import User
from app.models.movie import Movie, Genre
from app.models.interaction import Review, Watchlist