"""Initialise les tables et l'admin. À exécuter après chaque déploiement."""
import sys
import traceback

def main():
    try:
        from app.database import Base, engine, SessionLocal
        from app.models import User, Genre
        from app.auth import hash_password
        from app.config import settings

        print("🔧 Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées (ou existantes)")

        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.role == "admin").first()
            if not existing:
                admin = User(
                    email=settings.ADMIN_EMAIL,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                    role="admin",
                )
                db.add(admin)
                print(f"✅ Admin créé : {settings.ADMIN_EMAIL}")
            else:
                print(f"ℹ️  Admin existant : {existing.email}")

            genres_defaut = [
                "Action", "Animation", "Comédie", "Documentaire", 
                "Drame", "Fantastique", "Formation", "Horreur", 
                "Romance", "Suspense"
            ]
            for nom in genres_defaut:
                if not db.query(Genre).filter(Genre.nom == nom).first():
                    db.add(Genre(nom=nom))
            db.commit()
            print("✅ Genres initialisés")
        finally:
            db.close()

        print("🎉 Base initialisée avec succès")
        return 0

    except Exception:
        print("❌ ERREUR lors de l'initialisation :", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())