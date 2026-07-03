from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth, cartera, clientes, solicitudes, preevaluacion, buro,
    cobranza, alertas, campanas, reportes, cliente_app, notificaciones, supervisor,
)

app = FastAPI(
    title="Prymera — API Mobile",
    description="Backend FastAPI para App Fuerza de Ventas y App Cliente",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cartera.router)
app.include_router(clientes.router)
app.include_router(solicitudes.router)
app.include_router(preevaluacion.router)
app.include_router(buro.router)
app.include_router(cobranza.router)
app.include_router(alertas.router)
app.include_router(campanas.router)
app.include_router(reportes.router)
app.include_router(cliente_app.router)
app.include_router(notificaciones.router)
app.include_router(supervisor.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "Prymera API Mobile", "version": "1.0.0"}
