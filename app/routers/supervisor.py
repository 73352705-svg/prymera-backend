from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models import Asesor, Cliente, CarteraDiaria, Credito, SolicitudCredito, Agencia
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/supervisor", tags=["Supervisor"])


def get_supervisor(token: str = Header(alias="Authorization"), db: Session = Depends(get_db)) -> Asesor:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    asesor = db.query(Asesor).filter(Asesor.id == payload["sub"]).first()
    if not asesor or asesor.perfil != "supervisor":
        raise HTTPException(status_code=403, detail="Acceso solo para supervisores")
    return asesor


class ResumenDashboard(BaseModel):
    total_asesores_activos: int
    visitas_hoy: int
    pendientes: int
    solicitudes_enviadas: int
    solicitudes_aprobadas: int
    solicitudes_desembolsadas: int
    monto_total_desembolsado: float
    asesores: list["AsesorResumen"]
    actividad_reciente: list["ActividadItem"]

    class Config:
        from_attributes = True


class AsesorResumen(BaseModel):
    id: str
    codigo_empleado: str
    nombres: str
    apellidos: str
    agencia: Optional[str] = None
    visitas_hoy: int = 0
    total_asignados: int = 0
    ultima_sync: Optional[str] = None


class ActividadItem(BaseModel):
    asesor_nombre: str
    accion: str
    tiempo: str


@router.get("/resumen", response_model=ResumenDashboard)
def resumen_dashboard(supervisor: Asesor = Depends(get_supervisor), db: Session = Depends(get_db)):
    hoy = date.today()

    total_asesores_activos = db.query(Asesor).filter(Asesor.activo == True, Asesor.perfil == "operador").count()

    visitas_hoy = db.query(CarteraDiaria).filter(
        CarteraDiaria.fecha_asignacion == hoy,
        CarteraDiaria.estado_visita == "completado"
    ).count()

    pendientes = db.query(CarteraDiaria).filter(
        CarteraDiaria.fecha_asignacion == hoy,
        CarteraDiaria.estado_visita.in_(["pendiente", "en_curso"])
    ).count()

    solicitudes_enviadas = db.query(SolicitudCredito).filter(
        SolicitudCredito.created_at >= hoy
    ).count()

    solicitudes_aprobadas = db.query(SolicitudCredito).filter(
        SolicitudCredito.estado == "aprobado"
    ).count()

    solicitudes_desembolsadas = db.query(SolicitudCredito).filter(
        SolicitudCredito.estado == "desembolsado"
    ).count()

    monto_total = db.query(func.coalesce(func.sum(Credito.monto_desembolsado), 0)).scalar() or 0

    asesores_data = db.query(Asesor).filter(Asesor.activo == True, Asesor.perfil == "operador").all()
    asesores_lista = []
    for a in asesores_data:
        v_hoy = db.query(CarteraDiaria).filter(
            CarteraDiaria.asesor_id == a.id,
            CarteraDiaria.fecha_asignacion == hoy,
            CarteraDiaria.estado_visita == "completado"
        ).count()
        total_asig = db.query(CarteraDiaria).filter(
            CarteraDiaria.asesor_id == a.id,
            CarteraDiaria.fecha_asignacion == hoy
        ).count()
        agencia_nombre = db.query(Agencia.nombre).filter(Agencia.id == a.agencia_id).scalar() if a.agencia_id else None
        asesores_lista.append(AsesorResumen(
            id=str(a.id), codigo_empleado=a.codigo_empleado,
            nombres=a.nombres, apellidos=a.apellidos,
            agencia=agencia_nombre,
            visitas_hoy=v_hoy, total_asignados=total_asig,
        ))

    actividad = db.query(CarteraDiaria).filter(
        CarteraDiaria.fecha_asignacion == hoy,
        CarteraDiaria.estado_visita == "completado"
    ).order_by(CarteraDiaria.id.desc()).limit(10).all()

    actividad_lista = []
    for v in actividad:
        asesor = db.query(Asesor).filter(Asesor.id == v.asesor_id).first()
        cliente = db.query(Cliente).filter(Cliente.id == v.cliente_id).first()
        nombre = f"{asesor.nombres} {asesor.apellidos}" if asesor else "---"
        cliente_nombre = f"{cliente.nombres} {cliente.apellidos}" if cliente else "---"
        actividad_lista.append(ActividadItem(
            asesor_nombre=nombre,
            accion=f"Visito a {cliente_nombre}",
            tiempo="hoy"
        ))

    return ResumenDashboard(
        total_asesores_activos=total_asesores_activos,
        visitas_hoy=visitas_hoy,
        pendientes=pendientes,
        solicitudes_enviadas=solicitudes_enviadas,
        solicitudes_aprobadas=solicitudes_aprobadas,
        solicitudes_desembolsadas=solicitudes_desembolsadas,
        monto_total_desembolsado=float(monto_total),
        asesores=asesores_lista,
        actividad_reciente=actividad_lista,
    )
