from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from ..database import get_db
from ..models import Film, Genre, Episode, EpisodeType, User
from ..deps import require_admin, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


# ---------- Dashboard ----------
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    films = db.query(Film).order_by(Film.id.desc()).all()
    stats = {
        "total_films": db.query(Film).count(),
        "dispo": db.query(Film).filter(Film.status == True).count(),
        "indispo": db.query(Film).filter(Film.status == False).count(),
        "total_episodes": db.query(Episode).count(),
    }
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "admin": admin, "films": films, "stats": stats},
    )


# ---------- Créer un film ----------
@router.get("/films/new", response_class=HTMLResponse)
def film_new_page(
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    genres = db.query(Genre).order_by(Genre.nom).all()
    return templates.TemplateResponse(
        "film_form.html",
        {"request": request, "admin": admin, "film": None, "genres": genres},
    )


@router.post("/films/new")
def film_create(
    request: Request,
    titre: str = Form(...),
    image_cover: str = Form(...),
    description: str = Form(""),
    age_min: int = Form(0),
    annee: str = Form(""),
    status: str = Form("on"),  # checkbox => "on" si coché
    genres: list[int] = Form(default=[]),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = Film(
        titre=titre.strip(),
        image_cover=image_cover.strip(),
        description=description.strip(),
        age_min=age_min,
        annee=int(annee) if annee.strip() else None,
        status=(status == "on"),
    )
    if genres:
        film.genres = db.query(Genre).filter(Genre.id.in_(genres)).all()
    db.add(film)
    db.commit()
    db.refresh(film)
    return RedirectResponse(url=f"/admin/films/{film.id}", status_code=303)


# ---------- Modifier un film ----------
@router.get("/films/{film_id}/edit", response_class=HTMLResponse)
def film_edit_page(
    film_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if not film:
        raise HTTPException(404, "Film introuvable")
    genres = db.query(Genre).order_by(Genre.nom).all()
    return templates.TemplateResponse(
        "film_form.html",
        {"request": request, "admin": admin, "film": film, "genres": genres},
    )


@router.post("/films/{film_id}/edit")
def film_update(
    film_id: int,
    titre: str = Form(...),
    image_cover: str = Form(...),
    description: str = Form(""),
    age_min: int = Form(0),
    annee: str = Form(""),
    status: str = Form("off"),
    genres: list[int] = Form(default=[]),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if not film:
        raise HTTPException(404, "Film introuvable")

    film.titre = titre.strip()
    film.image_cover = image_cover.strip()
    film.description = description.strip()
    film.age_min = age_min
    film.annee = int(annee) if annee.strip() else None
    film.status = (status == "on")
    film.genres = db.query(Genre).filter(Genre.id.in_(genres)).all() if genres else []

    db.commit()
    return RedirectResponse(url=f"/admin/films/{film.id}", status_code=303)


# ---------- Supprimer un film ----------
@router.post("/films/{film_id}/delete")
def film_delete(
    film_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if film:
        db.delete(film)
        db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ---------- Détail film + liste épisodes ----------
@router.get("/films/{film_id}", response_class=HTMLResponse)
def film_detail(
    film_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if not film:
        raise HTTPException(404, "Film introuvable")
    return templates.TemplateResponse(
        "film_detail.html",
        {"request": request, "admin": admin, "film": film},
    )


# ---------- Ajouter une vidéo (épisode) ----------
@router.get("/films/{film_id}/episodes/new", response_class=HTMLResponse)
def episode_new_page(
    film_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if not film:
        raise HTTPException(404, "Film introuvable")
    return templates.TemplateResponse(
        "episode_form.html",
        {"request": request, "admin": admin, "film": film, "episode": None},
    )


@router.post("/films/{film_id}/episodes/new")
def episode_create(
    film_id: int,
    titre: str = Form(...),
    type: str = Form(...),  # "trailer" | "notrailer"
    lien: str = Form(...),
    ordre: int = Form(0),
    duration: str = Form(""),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    film = db.query(Film).get(film_id)
    if not film:
        raise HTTPException(404, "Film introuvable")

    if type not in ("trailer", "notrailer"):
        raise HTTPException(400, "Type invalide")

    ep = Episode(
        idfilm=film.id,
        titre=titre.strip(),
        type=EpisodeType(type),
        lien=lien.strip(),
        ordre=ordre,
        duration=duration.strip(),
    )
    db.add(ep)
    db.commit()
    return RedirectResponse(url=f"/admin/films/{film.id}", status_code=303)


# ---------- Modifier épisode ----------
@router.get("/episodes/{ep_id}/edit", response_class=HTMLResponse)
def episode_edit_page(
    ep_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ep = db.query(Episode).get(ep_id)
    if not ep:
        raise HTTPException(404, "Épisode introuvable")
    return templates.TemplateResponse(
        "episode_form.html",
        {"request": request, "admin": admin, "film": ep.film, "episode": ep},
    )


@router.post("/episodes/{ep_id}/edit")
def episode_update(
    ep_id: int,
    titre: str = Form(...),
    type: str = Form(...),
    lien: str = Form(...),
    ordre: int = Form(0),
    duration: str = Form(""),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ep = db.query(Episode).get(ep_id)
    if not ep:
        raise HTTPException(404, "Épisode introuvable")
    ep.titre = titre.strip()
    ep.type = EpisodeType(type)
    ep.lien = lien.strip()
    ep.ordre = ordre
    ep.duration = duration.strip()
    db.commit()
    return RedirectResponse(url=f"/admin/films/{ep.idfilm}", status_code=303)


@router.post("/episodes/{ep_id}/delete")
def episode_delete(
    ep_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ep = db.query(Episode).get(ep_id)
    if ep:
        fid = ep.idfilm
        db.delete(ep)
        db.commit()
        return RedirectResponse(url=f"/admin/films/{fid}", status_code=303)
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ---------- Genres ----------
@router.get("/genres", response_class=HTMLResponse)
def genres_list(
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    genres = db.query(Genre).order_by(Genre.nom).all()
    return templates.TemplateResponse(
        "genres.html",
        {"request": request, "admin": admin, "genres": genres},
    )


@router.post("/genres/new")
def genre_create(
    nom: str = Form(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    nom = nom.strip()
    if nom and not db.query(Genre).filter(Genre.nom == nom).first():
        db.add(Genre(nom=nom))
        db.commit()
    return RedirectResponse(url="/admin/genres", status_code=303)


@router.post("/genres/{gid}/delete")
def genre_delete(
    gid: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    g = db.query(Genre).get(gid)
    if g:
        db.delete(g)
        db.commit()
    return RedirectResponse(url="/admin/genres", status_code=303)