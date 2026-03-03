import httpx
import os
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.movie import Movie, Genre
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(url: str, params: dict, retries: int = 5) -> dict:
    params["api_key"] = TMDB_API_KEY
    for attempt in range(retries):
        try:
            time.sleep(1.5)
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = (attempt + 1) * 5
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            wait = (attempt + 1) * 5
            print(f"  Connection error attempt {attempt + 1}: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise Exception(f"Failed after {retries} attempts")


def fetch_popular_movies(pages: int = 10):
    db: Session = SessionLocal()
    total_added = 0

    for page in range(1, pages + 1):
        print(f"\nFetching page {page}/{pages}...")

        try:
            data = tmdb_get(f"{BASE_URL}/movie/popular", {"page": page})
        except Exception as e:
            print(f"  Could not fetch page {page}: {e}. Skipping page.")
            continue

        for item in data.get("results", []):
            if db.query(Movie).filter(Movie.id == item["id"]).first():
                print(f"  Skipping {item['title']} (already exists)")
                continue

            try:
                detail = tmdb_get(
                    f"{BASE_URL}/movie/{item['id']}",
                    {"append_to_response": "credits,release_dates"}
                )
            except Exception as e:
                print(f"  Could not fetch details for {item['title']}: {e}. Skipping.")
                continue

            # Extract director
            director = None
            crew = detail.get("credits", {}).get("crew", [])
            directors = [p["name"] for p in crew if p.get("job") == "Director"]
            if directors:
                director = directors[0]

            # Extract US certification
            certification = None
            for entry in detail.get("release_dates", {}).get("results", []):
                if entry.get("iso_3166_1") == "US":
                    for release in entry.get("release_dates", []):
                        cert = release.get("certification")
                        if cert:
                            certification = cert
                            break

            movie = Movie(
                id=item["id"],
                title=item["title"],
                overview=item.get("overview"),
                poster_path=item.get("poster_path"),
                backdrop_path=item.get("backdrop_path"),
                release_date=item.get("release_date"),
                vote_average=item.get("vote_average"),
                original_language=item.get("original_language"),
                runtime=detail.get("runtime"),
                director=director,
                certification=certification,
            )

            # Fix: commit each genre individually so duplicates are never batched
            for g in detail.get("genres", []):
                genre = db.query(Genre).filter(Genre.id == g["id"]).first()
                if not genre:
                    genre = Genre(id=g["id"], name=g["name"])
                    db.add(genre)
                    db.commit()
                    db.refresh(genre)
                movie.genres.append(genre)

            # Commit each movie individually
            try:
                db.add(movie)
                db.commit()
                total_added += 1
                print(f"  Added: {item['title']}")
            except Exception as e:
                print(f"  Failed to add {item['title']}: {e}. Skipping.")
                db.rollback()

        print(f"Page {page} done. Total so far: {total_added}")

    db.close()
    print(f"\nIngestion complete! Added {total_added} movies.")


if __name__ == "__main__":
    fetch_popular_movies(pages=10)