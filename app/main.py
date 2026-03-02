from fastapi import FastAPI
from app.routers import auth, movies, reviews, watchlist

app = FastAPI(title="Movie App API", version="1.0.0")

# Register all routers — like @RequestMapping at the class level in Spring
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(reviews.router)
app.include_router(watchlist.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}