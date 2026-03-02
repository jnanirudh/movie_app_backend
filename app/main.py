from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, movies, reviews, watchlist

app = FastAPI(
    title="Movie App API",
    description="Backend for the Flutter movie reviewing app",
    version="1.0.0",
    docs_url="/docs",       # http://localhost:8000/docs
    redoc_url="/redoc",     # http://localhost:8000/redoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(reviews.router)
app.include_router(watchlist.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Quick check that the server is running."""
    return {"status": "ok", "version": "1.0.0"}