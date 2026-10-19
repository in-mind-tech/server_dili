from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


# ---- Relation N-N films <-> genres ----
film_genres = Table(
    "film_genres",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    device_id = Column(String(255), unique=True, index=True, nullable=True) # <-- NOUVEAU
    email = Column(String(255), unique=True, nullable=True) # Devient optionnel
    password_hash = Column(String(255), nullable=True)      # Devient optionnel
    role = Column(String(20), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    nom = Column(String(50), unique=True, nullable=False)


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True)
    titre = Column(String(255), nullable=False)
    image_cover = Column(String(500), nullable=False)
    description = Column(Text, default="")
    status = Column(Boolean, default=True)  # True = disponible
    age_min = Column(Integer, default=0)
    annee = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    genres = relationship("Genre", secondary=film_genres, lazy="selectin")
    episodes = relationship(
        "Episode", back_populates="film",
        cascade="all, delete-orphan", lazy="selectin"
    )


class EpisodeType(str, enum.Enum):
    trailer = "trailer"
    notrailer = "notrailer"


class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    idfilm = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    titre = Column(String(255), nullable=False)
    type = Column(Enum(EpisodeType), nullable=False)
    lien = Column(String(500), nullable=False)  # YouTube URL OU Bunny video ID
    ordre = Column(Integer, default=0)
    duration = Column(String(20), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    film = relationship("Film", back_populates="episodes")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    platform = Column(String(20))  # "google" | "apple"
    product_id = Column(String(50))  # sub_daily | sub_weekly | sub_monthly
    original_transaction_id = Column(String(255), unique=True)
    receipt = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())