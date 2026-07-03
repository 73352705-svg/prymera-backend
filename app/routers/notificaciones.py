from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Notificacion

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("")
def listar_notificaciones(asesor_id: str | None = None, cliente_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Notificacion)
    if asesor_id:
        query = query.filter(Notificacion.asesor_id == asesor_id)
    if cliente_id:
        query = query.filter(Notificacion.cliente_id == cliente_id)
    notis = query.order_by(Notificacion.created_at.desc()).limit(30).all()
    return [
        {
            "id": str(n.id),
            "titulo": n.titulo,
            "cuerpo": n.cuerpo,
            "tipo": n.tipo,
            "leida": n.leida,
            "created_at": n.created_at.isoformat(),
        }
        for n in notis
    ]


@router.post("/{notificacion_id}/leer")
def marcar_leida(notificacion_id: str, db: Session = Depends(get_db)):
    noti = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if noti:
        noti.leida = True
        db.commit()
    return {"ok": True}
