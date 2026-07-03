from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CampanaActiva, Cliente
from app.schemas import CampanaOut

router = APIRouter(prefix="/campanas", tags=["Campanas"])


@router.get("", response_model=list[CampanaOut])
def listar_campanas(asesor_id: str, db: Session = Depends(get_db)):
    campanas = (
        db.query(CampanaActiva)
        .filter(CampanaActiva.asesor_id == asesor_id, CampanaActiva.activa == True)
        .order_by(CampanaActiva.fecha_vencimiento.asc())
        .all()
    )
    result = []
    for c in campanas:
        cliente = db.query(Cliente).filter(Cliente.id == c.cliente_id).first()
        result.append(
            CampanaOut(
                id=str(c.id),
                cliente_id=str(c.cliente_id),
                cliente_nombre=f"{cliente.nombres} {cliente.apellidos}" if cliente else "---",
                tipo=c.tipo,
                monto_ofertado=c.monto_ofertado,
                fecha_vencimiento=c.fecha_vencimiento,
            )
        )
    return result
