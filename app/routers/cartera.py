from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CarteraDiaria, Asesor, Cliente
from app.schemas import CarteraItemOut, VisitaUpdate

router = APIRouter(prefix="/cartera", tags=["Cartera"])


@router.get("", response_model=list[CarteraItemOut])
def listar_cartera(asesor_id: str, fecha: str | None = None, db: Session = Depends(get_db)):
    hoy = date.fromisoformat(fecha) if fecha else date.today()
    items = (
        db.query(CarteraDiaria)
        .filter(CarteraDiaria.asesor_id == asesor_id, CarteraDiaria.fecha_asignacion == hoy)
        .order_by(CarteraDiaria.score_prioridad.desc())
        .all()
    )
    result = []
    for item in items:
        cliente = db.query(Cliente).filter(Cliente.id == item.cliente_id).first()
        doc = cliente.numero_documento if cliente else ""
        doc_censurado = f"***{doc[-3:]}" if len(doc) >= 3 else doc
        result.append(
            CarteraItemOut(
                id=str(item.id),
                cliente_id=str(item.cliente_id),
                cliente_nombre=f"{cliente.nombres} {cliente.apellidos}" if cliente else "---",
                documento=doc_censurado,
                tipo_gestion=item.tipo_gestion,
                prioridad=item.prioridad,
                score_prioridad=item.score_prioridad,
                monto_credito=item.monto_credito,
                estado_visita=item.estado_visita,
                resultado_visita=item.resultado_visita,
                observacion_visita=item.observacion_visita,
                lat_visita=item.lat_visita,
                lng_visita=item.lng_visita,
                orden_manual=item.orden_manual,
            )
        )
    return result


@router.post("/{cartera_id}/visita")
def registrar_visita(cartera_id: str, data: VisitaUpdate, db: Session = Depends(get_db)):
    item = db.query(CarteraDiaria).filter(CarteraDiaria.id == cartera_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item de cartera no encontrado")
    item.estado_visita = data.estado_visita
    item.resultado_visita = data.resultado_visita
    item.observacion_visita = data.observacion_visita
    if data.lat is not None:
        item.lat_visita = data.lat
    if data.lng is not None:
        item.lng_visita = data.lng
    db.commit()
    return {"ok": True}
