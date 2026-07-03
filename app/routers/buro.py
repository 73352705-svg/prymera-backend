from fastapi import APIRouter
from app.schemas import BuroRequest, BuroResponse

router = APIRouter(prefix="/buro", tags=["Buro"])


@router.post("/consulta", response_model=BuroResponse)
def consultar_buro(data: BuroRequest):
    dni = data.numero_documento
    if len(dni) != 8:
        return BuroResponse(
            calificacion_sbs="---",
            entidades_con_deuda=0,
            deuda_total_pen=0,
            mayor_deuda=0,
            dias_mayor_mora=0,
            en_lista_negra=True,
            motivo_bloqueo="Documento invalido",
            interpretacion="El documento ingresado no es valido.",
        )

    ultimo = int(dni[-1])
    if ultimo >= 7:
        return BuroResponse(
            calificacion_sbs="Normal",
            entidades_con_deuda=2,
            deuda_total_pen=15400.00,
            mayor_deuda=12000.00,
            dias_mayor_mora=0,
            en_lista_negra=False,
            interpretacion="El cliente tiene historial en dos entidades con deuda total de S/15,400. Sin mora historica. Recomendacion: proceder con la evaluacion.",
        )
    elif ultimo >= 4:
        return BuroResponse(
            calificacion_sbs="CPP",
            entidades_con_deuda=3,
            deuda_total_pen=28500.00,
            mayor_deuda=15000.00,
            dias_mayor_mora=15,
            en_lista_negra=False,
            interpretacion="El cliente tiene historial en tres entidades con deuda total de S/28,500. Presenta mora de 15 dias. Recomendacion: revision adicional.",
        )
    else:
        return BuroResponse(
            calificacion_sbs="Deficiente",
            entidades_con_deuda=4,
            deuda_total_pen=45000.00,
            mayor_deuda=20000.00,
            dias_mayor_mora=45,
            en_lista_negra=True,
            motivo_bloqueo="Cliente registrado en lista de alerta temprana",
            interpretacion="El cliente presenta deuda significativa en cuatro entidades con mora de 45 dias. Se encuentra en lista de restriccion.",
        )
