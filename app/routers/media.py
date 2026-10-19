import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from ..models import User, Subscription
from ..config import settings

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/{video_id}/token")
def bunny_token(
    video_id: str, 
    x_device_id: str = Header(...), # L'application Flutter enverra cet en-tête
    db: Session = Depends(get_db)
):
    # 1. Trouver l'utilisateur via son Device ID
    user = db.query(User).filter(User.device_id == x_device_id).first()
    
    # Si l'appareil n'existe pas, on le crée automatiquement
    if not user:
        user = User(device_id=x_device_id, role="user")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Vérifier si l'abonnement est actif
    # (Pour l'instant on autorise tout le monde pour tester, on rajoutera la vérif plus tard)
    
    # 3. Générer le token Bunny
    bunny_key = settings.BUNNY_KEY
    expires = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
    raw = f"{bunny_key}{video_id}{expires}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    
    return {"token": token, "expires": expires}