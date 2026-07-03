from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SolicitudCredito, SolicitudNotaInterna, Asesor
from app.schemas import SolicitudCreate, SolicitudOut, SolicitudResumen

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post("", response_model=SolicitudOut)
def crear_solicitud(data: SolicitudCreate, asesor_id: str, db: Session = Depends(get_db)):
    solicitud = SolicitudCredito(
        asesor_id=asesor_id,
        cliente_id=data.cliente_id,
        monto_solicitado=data.monto_solicitado,
        plazo_meses=data.plazo_meses,
        tipo_negocio=data.tipo_negocio,
        nombre_negocio=data.nombre_negocio,
        destino_credito=data.destino_credito,
        moneda=data.moneda,
        tipo_cuota=data.tipo_cuota,
        garantia=data.garantia,
        firma_cliente_base64=data.firma_cliente_base64,
        lat_captura=data.lat,
        lng_captura=data.lng,
        estado="enviado",
        numero_expediente=f"EXP-{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}-{str(asesor_id)[:4]}",
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return SolicitudOut(
        id=str(solicitud.id),
        numero_expediente=solicitud.numero_expediente,
        cliente_id=str(solicitud.cliente_id),
        monto_solicitado=solicitud.monto_solicitado,
        estado=solicitud.estado,
        created_at=solicitud.created_at,
    )


@router.get("", response_model=list[SolicitudResumen])
def listar_solicitudes(asesor_id: str, db: Session = Depends(get_db)):
    solicitudes = (
        db.query(SolicitudCredito)
        .filter(SolicitudCredito.asesor_id == asesor_id)
        .order_by(SolicitudCredito.created_at.desc())
        .all()
    )
    hoy = datetime.now(timezone.utc)
    return [
        SolicitudResumen(
            id=str(s.id),
            cliente_nombre=s.cliente_id or "---",
            monto_solicitado=s.monto_solicitado,
            estado=s.estado,
            dias_desde_envio=(hoy - s.created_at).days if s.created_at else 0,
            analista_asignado=s.analista_asignado,
        )
        for s in solicitudes
    ]


@router.post("/{solicitud_id}/notas")
def agregar_nota(solicitud_id: str, contenido: str, asesor_id: str, db: Session = Depends(get_db)):
    if len(contenido) > 500:
        raise HTTPException(status_code=400, detail="Maximo 500 caracteres")
    nota = SolicitudNotaInterna(
        solicitud_id=solicitud_id,
        asesor_id=asesor_id,
        contenido=contenido,
    )
    db.add(nota)
    db.commit()
    return {"ok": True}
