import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException

from ..config import settings
from ..deps import require_user

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/{video_id}/token")
def bunny_token(video_id: str, user=Depends(require_user)):
    """
    Génère un token Bunny signé. Le BUNNY_KEY n'est JAMAIS exposé.
    Format validé : sha256(KEY + videoId + expires)
    """
    expires = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
    raw = f"{settings.BUNNY_KEY}{video_id}{expires}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    url = (
        f"https://iframe.mediadelivery.net/embed/"
        f"{settings.BUNNY_LIB}/{video_id}?token={token}&expires={expires}"
    )
    return {"token": token, "expires": expires, "embed_url": url}