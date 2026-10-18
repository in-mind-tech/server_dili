from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.database import get_db
from ..database import get_db
from ..models import User
from ..auth import verify_password, create_access_token
from ..schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")


# --- API JSON (mobile) ---
@router.post("/login", response_model=Token)
def api_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token}


# --- Formulaire HTML (dashboard) ---
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login-form")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Identifiants invalides"},
            status_code=401,
        )
    if user.role != "admin":
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Accès admin requis"},
            status_code=403,
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(
        "access_token", token, httponly=True, samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response