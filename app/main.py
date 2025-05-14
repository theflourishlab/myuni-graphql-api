import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schemas import Query # Import your Query definition
from .database import Base, engine # Import Base and engine for migrations

# Create DB tables if they don't exist (use Alembic for production)
# Base.metadata.create_all(bind=engine) # Comment out if using Alembic manages tables

# Create the GraphQL schema
schema = strawberry.Schema(query=Query) # Add mutation=Mutation if you have mutations

# Create the GraphQL router
graphql_app = GraphQLRouter(schema)

# Create the FastAPI app
app = FastAPI(title="FindMyUni API")

# Include the GraphQL router
app.include_router(graphql_app, prefix="/graphql")

# Simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FindMyUni API. Go to /graphql for the GraphQL interface."}

# --- Alembic Setup ---
# 1. Install alembic: pip install alembic
# 2. Initialize: alembic init alembic
# 3. Configure alembic/env.py:
#    - Set `target_metadata = Base.metadata` (import Base from your models)
#    - Configure `sqlalchemy.url = DATABASE_URL` (import from core.config)
# 4. Generate migration: alembic revision --autogenerate -m "Initial university table"
# 5. Apply migration: alembic upgrade head