from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Film, Episode, EpisodeType
from ..schemas import FilmOut, EpisodeOut

router = APIRouter(prefix="/films", tags=["films"])

# 1. Liste avec pagination
@router.get("", response_model=List[FilmOut])
def list_films(
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return db.query(Film).filter(Film.status == True)\
             .order_by(Film.id.desc())\
             .offset(skip).limit(limit).all()

# 2. Détails d'un film
@router.get("/{film_id}", response_model=FilmOut)
def film_detail(film_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.id == film_id, Film.status == True).first()
    if not film:
        raise HTTPException(404, "Film introuvable")
    return film

# 3. Épisodes d'un film (PUBLIC pour l'instant)
@router.get("/{film_id}/episodes", response_model=List[EpisodeOut])
def film_episodes(
    film_id: int,
    db: Session = Depends(get_db),
):
    # On ne filtre plus par abonnement. 
    # On renvoie TOUS les épisodes (trailer + notrailer).
    # Le contrôle d'accès au film Bunny se fera via le Token.
    eps = db.query(Episode).filter(Episode.idfilm == film_id)\
            .order_by(Episode.ordre).all()
    return eps