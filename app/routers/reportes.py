from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import SolicitudCredito, Asesor
from app.schemas import ReporteProductividad

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/productividad", response_model=list[ReporteProductividad])
def productividad_mensual(agencia_id: str | None = None, db: Session = Depends(get_db)):
    hoy = datetime.now(timezone.utc)
    query = (
        db.query(
            SolicitudCredito.asesor_id,
            func.count().label("total"),
            SolicitudCredito.estado,
        )
        .filter(
            func.extract("month", SolicitudCredito.created_at) == hoy.month,
            func.extract("year", SolicitudCredito.created_at) == hoy.year,
        )
        .group_by(SolicitudCredito.asesor_id, SolicitudCredito.estado)
    )

    if agencia_id:
        asesores_agencia = db.query(Asesor.id).filter(Asesor.agencia_id == agencia_id).subquery()
        query = query.filter(SolicitudCredito.asesor_id.in_(asesores_agencia))

    rows = query.all()
    asesores_data = {}
    for row in rows:
        aid = str(row.asesor_id)
        if aid not in asesores_data:
            asesor = db.query(Asesor).filter(Asesor.id == row.asesor_id).first()
            asesores_data[aid] = {
                "nombre": f"{asesor.nombres} {asesor.apellidos}" if asesor else "---",
                "enviadas": 0,
                "aprobadas": 0,
                "desembolsadas": 0,
                "monto_total": 0.0,
            }
        if row.estado == "enviado":
            asesores_data[aid]["enviadas"] += row.total
        elif row.estado == "aprobado":
            asesores_data[aid]["aprobadas"] += row.total
        elif row.estado == "desembolsado":
            asesores_data[aid]["desembolsadas"] += row.total

    result = []
    for aid, d in asesores_data.items():
        total = d["enviadas"] or 1  # evitar division por cero
        result.append(
            ReporteProductividad(
                asesor_nombre=d["nombre"],
                enviadas=d["enviadas"],
                aprobadas=d["aprobadas"],
                desembolsadas=d["desembolsadas"],
                monto_total=d["monto_total"],
                tasa_aprobacion=round(d["aprobadas"] / total * 100, 1),
            )
        )
    return result
