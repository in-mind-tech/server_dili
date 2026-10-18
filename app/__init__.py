"""
Lancer une fois : python init_db.py
Crée les tables + un admin par défaut + quelques genres.
"""
from app.database import Base, engine, SessionLocal
from app.models import User, Genre
from app.auth import hash_password
from app.config import settings

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not db.query(User).filter(User.role == "admin").first():
        admin = User(
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin)
        print(f"✅ Admin créé : {settings.ADMIN_EMAIL}")
    else:
        print("ℹ️  Admin déjà existant")

    for nom in ["Action", "Comédie", "Drame", "Horreur", "Science-Fiction", "Animation"]:
        if not db.query(Genre).filter(Genre.nom == nom).first():
            db.add(Genre(nom=nom))

    db.commit()
    db.close()
    print("✅ Base initialisée")


if __name__ == "__main__":
    main()