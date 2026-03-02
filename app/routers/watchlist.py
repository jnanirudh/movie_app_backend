@router.get("/", response_model=list[WatchlistOut])
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's watchlist with full movie details from your database.
    No TMDB calls needed — movie data is already stored locally.
    """
    entries = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .all()
    )

    result = []
    for entry in entries:
        if entry.movie:  # movie is loaded via SQLAlchemy relationship
            result.append(WatchlistOut(movie=entry.movie, added_at=entry.added_at))
    return result