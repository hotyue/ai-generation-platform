from backend.app.database import Base, engine
from backend.app.models.user import User
from backend.app.models.history import History

print("Dropping and creating database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database initialization complete.")
