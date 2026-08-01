from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.base import Base, engine

from routes.extraction import verification_router
from routes.community import community_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(verification_router)
app.include_router(community_router)

