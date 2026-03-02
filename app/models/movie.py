from sqlalchemy import Column, Integer, String, Text, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Pure join table for Movie <-> Genre many-to-many
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)  # TMDB genre id — no auto-increment
    name = Column(String, nullable=False)

    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)  # TMDB movie id — no auto-increment
    title = Column(String, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String, nullable=True)    # Store path only e.g. /abc123.jpg
    backdrop_path = Column(String, nullable=True)
    release_date = Column(String, nullable=True)   # "YYYY-MM-DD"
    vote_average = Column(Float, nullable=True)    # TMDB community rating 0-10
    original_language = Column(String, nullable=True)
    runtime = Column(Integer, nullable=True)       # Minutes
    director = Column(String, nullable=True)
    certification = Column(String, nullable=True)  # "PG-13", "R", etc.

    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    reviews = relationship("Review", back_populates="movie")
    watchlisted_by = relationship("Watchlist", back_populates="movie")