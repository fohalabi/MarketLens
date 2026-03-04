from app.database import engine, Base

# Import all models to ensure they are registered with SQLAlchemy before creating tables
from app.models.stock import Stock
from app.models.portfolio import Portfolio
from app.models.alert import Alert


def init_db():
    """
    Creates all database tables if they don't exist.
    Like running mongoose.connect() — sets up the schema.
    Called when the app starts.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()