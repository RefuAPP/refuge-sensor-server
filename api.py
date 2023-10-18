import psycopg2
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from routers import refugios, sensors
from setup_database import Configuration
from starlette.middleware.cors import CORSMiddleware


DB_NAME = Configuration.get("DB_NAME")
DB_USER = Configuration.get("DB_USER")
DB_PASS = Configuration.get("DB_PASS")
DB_HOST = Configuration.get("DB_HOST")
DB_PORT = Configuration.get("DB_PORT")

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

app = FastAPI()

# Incluye los routers
app.include_router(refugios.router)
app.include_router(sensors.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def root():
    return RedirectResponse(url='/docs')
