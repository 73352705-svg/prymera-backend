from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import AlertaCartera, Cliente
from app.schemas import AlertaOut

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("", response_model=list[AlertaOut])
def listar_alertas(asesor_id: str, db: Session = Depends(get_db)):
    alertas = (
        db.query(AlertaCartera)
        .filter(AlertaCartera.asesor_id == asesor_id)
        .order_by(AlertaCartera.created_at.desc())
        .all()
    )
    return [
        AlertaOut(
            id=str(a.id),
            cliente_id=str(a.cliente_id),
            tipo_alerta=a.tipo_alerta,
            mensaje=a.mensaje,
            leida=a.leida,
            created_at=a.created_at,
        )
        for a in alertas
    ]


@router.get("/no-leidas", response_model=list[AlertaOut])
def alertas_no_leidas(asesor_id: str, db: Session = Depends(get_db)):
    alertas = (
        db.query(AlertaCartera)
        .filter(AlertaCartera.asesor_id == asesor_id, AlertaCartera.leida == False)
        .order_by(AlertaCartera.created_at.desc())
        .all()
    )
    return [
        AlertaOut(
            id=str(a.id),
            cliente_id=str(a.cliente_id),
            tipo_alerta=a.tipo_alerta,
            mensaje=a.mensaje,
            leida=a.leida,
            created_at=a.created_at,
        )
        for a in alertas
    ]


@router.post("/{alerta_id}/leer")
def marcar_leida(alerta_id: str, db: Session = Depends(get_db)):
    alerta = db.query(AlertaCartera).filter(AlertaCartera.id == alerta_id).first()
    if alerta:
        alerta.leida = True
        db.commit()
    return {"ok": True}
