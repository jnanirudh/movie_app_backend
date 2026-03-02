import httpx, os
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.movie import Movie, Genre
from app.models.user import User
from app.models.interaction import Review, Watchlist
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def fetch_popular_movies(pages: int = 10):
    """Fetch `pages` pages of popular movies from TMDB (~200 movies per run)"""
    Base.metadata.create_all(bind=engine)  # Create tables if not exist
    db: Session = SessionLocal()

    for page in range(1, pages + 1):
        res = httpx.get(f"{BASE_URL}/movie/popular", params={"api_key": TMDB_API_KEY, "page": page})
        data = res.json()

        for item in data["results"]:
            if db.query(Movie).filter(Movie.id == item["id"]).first():
                continue  # Skip if already exists

            # Fetch full details for genres
            detail = httpx.get(f"{BASE_URL}/movie/{item['id']}", params={"api_key": TMDB_API_KEY}).json()

            movie = Movie(
                id=item["id"],
                title=item["title"],
                overview=item.get("overview"),
                poster_path=item.get("poster_path"),
                backdrop_path=item.get("backdrop_path"),
                release_date=item.get("release_date"),
                vote_average=item.get("vote_average"),
                original_language=item.get("original_language"),
            )

            for g in detail.get("genres", []):
                genre = db.query(Genre).filter(Genre.id == g["id"]).first()
                if not genre:
                    genre = Genre(id=g["id"], name=g["name"])
                    db.add(genre)
                movie.genres.append(genre)

            db.add(movie)

        db.commit()
        print(f"Page {page} done")

    db.close()
    print("Ingestion complete!")

if __name__ == "__main__":
    fetch_popular_movies(pages=10)