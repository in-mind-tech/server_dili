import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from ..config import settings
from ..deps import require_user # On garde l'import pour plus tard

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/{video_id}/token")
def bunny_token(video_id: str):
    """
    Génère un token Bunny signé.
    NOTE: La sécurité (Depends(require_user)) est retirée temporairement 
    pour permettre les tests de l'application mobile sans login.
    """
    try:
        # On récupère la clé depuis les variables d'environnement (Render)
        bunny_key = settings.BUNNY_KEY
        if not bunny_key:
            raise ValueError("BUNNY_KEY non configurée sur le serveur")

        # Calcul de l'expiration (10 minutes)
        expires = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
        
        # Signature SHA256 (Key + VideoID + Expires)
        raw_signature = f"{bunny_key}{video_id}{expires}"
        token = hashlib.sha256(raw_signature.encode()).hexdigest()
        
        return {"token": token, "expires": expires}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération token: {str(e)}")

# ⚠️ POUR LA SUITE (Quand le login sera fait), le code ressemblera à ça :
# @router.get("/{video_id}/token")
# def bunny_token_protected(video_id: str, user=Depends(require_user)):
#     # ... même code de génération ...