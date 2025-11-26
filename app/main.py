from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, seed_data, SessionLocal
from app.routers import bureau, prestamos

app = FastAPI(
    title="API Test Cases - Clase 2",
    description="API REST para ejecutar test cases de Bureau, Préstamos y Transferencias",
    version="1.0.0"
)

# CORS para permitir llamadas desde Angular (Clase 8)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event: Al iniciar API
@app.on_event("startup")
def startup_event():
    """Crea tablas e inserta datos demo en memoria"""
    print("🚀 Inicializando base de datos en memoria...")
    init_db()
    
    # Seed inicial
    db = SessionLocal()
    seed_data(db)
    db.close()

# Incluir routers
app.include_router(bureau.router)
app.include_router(prestamos.router)

@app.get("/")
def root():
    return {
        "message": "API Test Cases - Clase 2",
        "docs": "/docs",
        "endpoints": {
            "bureau": "/api/bureau/consultar",
            "prestamos": "/api/prestamos/solicitar"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "OK", "database": "SQLite in-memory"}
