from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Film, Episode, EpisodeType, Subscription
from ..schemas import FilmOut, FilmDetail, EpisodeOut
from ..deps import require_user, get_current_user
from datetime import datetime

router = APIRouter(prefix="/films", tags=["films"])


@router.get("", response_model=List[FilmOut])
def list_films(
    genre: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Film).filter(Film.status == True)
    if genre:
        query = query.join(Film.genres).filter_by(nom=genre)
    if q:
        like = f"%{q}%"
        query = query.filter(Film.titre.ilike(like) | Film.description.ilike(like))
    return query.order_by(Film.id.desc()).all()


@router.get("/{film_id}", response_model=FilmDetail)
def film_detail(film_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.id == film_id, Film.status == True).first()
    if not film:
        raise HTTPException(404, "Film introuvable")

    # On ne renvoie QUE le trailer ici
    film.episodes = [e for e in film.episodes if e.type == EpisodeType.trailer]
    return film


@router.get("/{film_id}/episodes", response_model=List[EpisodeOut])
def film_episodes(
    film_id: int,
    user=Depends(require_user),
    db: Session = Depends(get_db),
):
    """Renvoie les notrailer SEULEMENT si abonnement actif."""
    # Vérif abonnement
    sub = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.utcnow(),
        )
        .order_by(Subscription.expires_at.desc())
        .first()
    )
    if not sub:
        raise HTTPException(403, "Abonnement requis")

    eps = (
        db.query(Episode)
        .filter(Episode.idfilm == film_id, Episode.type == EpisodeType.notrailer)
        .order_by(Episode.ordre)
        .all()
    )
    return eps