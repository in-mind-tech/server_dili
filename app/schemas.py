from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    class Config:
        from_attributes = True


class GenreOut(BaseModel):
    id: int
    nom: str
    class Config:
        from_attributes = True


class EpisodeOut(BaseModel):
    id: int
    titre: str
    type: str
    lien: str
    ordre: int
    duration: str
    class Config:
        from_attributes = True


class FilmOut(BaseModel):
    id: int
    titre: str
    image_cover: str
    description: str
    status: bool
    age_min: int
    annee: Optional[int]
    genres: List[GenreOut] = []
    class Config:
        from_attributes = True


class FilmDetail(FilmOut):
    episodes: List[EpisodeOut] = []