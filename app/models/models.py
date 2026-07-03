import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, Text, Date, DateTime, JSON, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


def _uuid():
    return uuid.uuid4()


def _now():
    return datetime.now(timezone.utc)


class Agencia(Base):
    __tablename__ = "agencias"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cod_agencia = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    region = Column(String(50))
    lat = Column(Float)
    lng = Column(Float)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class Asesor(Base):
    __tablename__ = "asesores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cod_asesor = Column(String(20), unique=True)
    codigo_empleado = Column(String(10), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    agencia_id = Column(UUID(as_uuid=True), ForeignKey("agencias.id"))
    perfil = Column(String(20), default="operador")
    password_hash = Column(Text, nullable=False)
    token_fcm = Column(Text)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime(timezone=True))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    agencia = relationship("Agencia")


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cod_cliente = Column(String(20), unique=True)
    numero_documento = Column(String(15), unique=True, nullable=False)
    tipo_documento = Column(String(5), default="DNI")
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date)
    estado_civil = Column(String(15))
    telefono = Column(String(15))
    email = Column(String(100))
    direccion = Column(Text)
    tipo_negocio = Column(String(30))
    nombre_negocio = Column(String(100))
    antiguedad_negocio_meses = Column(Integer)
    ingresos_estimados = Column(Float)
    lat = Column(Float)
    lng = Column(Float)
    calificacion_sbs = Column(String(15))
    es_prospecto = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Credito(Base):
    __tablename__ = "cr_creditos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cod_cuenta_credito = Column(String(30), unique=True, nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    producto = Column(String(40))
    monto_desembolsado = Column(Float)
    saldo_capital = Column(Float)
    saldo_total = Column(Float)
    dias_mora = Column(Integer, default=0)
    calificacion_interna = Column(String(20))
    estado = Column(String(20))
    fecha_desembolso = Column(Date)
    tea = Column(Float)
    cuotas_total = Column(Integer)
    cuotas_pagadas = Column(Integer)
    sync_at = Column(DateTime(timezone=True), default=_now)


class CreditoPreaprobado(Base):
    __tablename__ = "creditos_preaprobados"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"))
    monto_maximo = Column(Float, nullable=False)
    plazo_sugerido_meses = Column(Integer)
    tea_referencial = Column(Float)
    score_confianza = Column(Integer)
    vigente = Column(Boolean, default=True)
    fecha_calculo = Column(Date)
    fecha_vencimiento = Column(Date)
    created_at = Column(DateTime(timezone=True), default=_now)


class CarteraDiaria(Base):
    __tablename__ = "cartera_diaria"
    __table_args__ = (
        UniqueConstraint("asesor_id", "cliente_id", "fecha_asignacion"),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    agencia_id = Column(UUID(as_uuid=True), ForeignKey("agencias.id"))
    fecha_asignacion = Column(Date, nullable=False)
    tipo_gestion = Column(String(30), nullable=False)
    prioridad = Column(String(10), default="normal")
    score_prioridad = Column(Integer, default=0)
    monto_credito = Column(Float)
    estado_visita = Column(String(20), default="pendiente")
    resultado_visita = Column(String(30))
    observacion_visita = Column(Text)
    timestamp_visita = Column(DateTime(timezone=True))
    lat_visita = Column(Float)
    lng_visita = Column(Float)
    orden_manual = Column(Integer)


class CampanaActiva(Base):
    __tablename__ = "campanas_activas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    tipo = Column(String(30))
    monto_ofertado = Column(Float)
    fecha_vencimiento = Column(Date)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class SolicitudCredito(Base):
    __tablename__ = "solicitudes_credito"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    numero_expediente = Column(String(20), unique=True)
    cod_solicitud_core = Column(String(20))
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    agencia_id = Column(UUID(as_uuid=True), ForeignKey("agencias.id"))
    canal = Column(String(15), default="asesor")
    tipo_negocio = Column(String(30))
    nombre_negocio = Column(String(100))
    actividad_economica = Column(String(10))
    antiguedad_negocio_meses = Column(Integer)
    ingresos_estimados = Column(Float)
    gastos_mensuales = Column(Float)
    patrimonio_estimado = Column(Float)
    tiene_conyuge = Column(Boolean, default=False)
    conyuge_json = Column(JSON)
    tiene_garante = Column(Boolean, default=False)
    garante_json = Column(JSON)
    monto_solicitado = Column(Float, nullable=False)
    plazo_meses = Column(Integer)
    moneda = Column(String(3), default="PEN")
    tipo_cuota = Column(String(10), default="mensual")
    garantia = Column(String(20))
    destino_credito = Column(Text)
    cuota_estimada = Column(Float)
    tea_referencial = Column(Float)
    estado = Column(String(30), default="borrador")
    monto_aprobado = Column(Float)
    motivo_rechazo = Column(Text)
    condicion_adicional = Column(Text)
    analista_asignado = Column(String(100))
    firma_cliente_base64 = Column(Text)
    lat_captura = Column(Float)
    lng_captura = Column(Float)
    pendiente_sync = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class SolicitudDocumento(Base):
    __tablename__ = "solicitudes_documentos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id", ondelete="CASCADE"), nullable=False)
    tipo_documento = Column(String(40), nullable=False)
    storage_url = Column(Text)
    tamanio_kb = Column(Integer)
    nitidez_score = Column(Float)
    created_at = Column(DateTime(timezone=True), default=_now)


class ConsultaBuro(Base):
    __tablename__ = "consultas_buro"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id"))
    dni_consultado = Column(String(15), nullable=False)
    calificacion_sbs = Column(String(20))
    entidades_con_deuda = Column(Integer)
    deuda_total_pen = Column(Float)
    mayor_deuda = Column(Float)
    dias_mayor_mora = Column(Integer)
    en_lista_negra = Column(Boolean, default=False)
    motivo_bloqueo = Column(Text)
    resultado_json = Column(JSON)
    firma_consentimiento_base64 = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_now)


class AccionCobranza(Base):
    __tablename__ = "acciones_cobranza"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    cod_cuenta_credito = Column(String(30), ForeignKey("cr_creditos.cod_cuenta_credito"))
    tipo_gestion = Column(String(20))
    resultado = Column(String(30))
    monto_pagado = Column(Float)
    fecha_compromiso = Column(Date)
    monto_compromiso = Column(Float)
    observaciones = Column(Text)
    lat = Column(Float)
    lng = Column(Float)
    timestamp_gestion = Column(DateTime(timezone=True), default=_now)
    pendiente_sync = Column(Boolean, default=False)


class AlertaCartera(Base):
    __tablename__ = "alertas_cartera"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    tipo_alerta = Column(String(30))
    mensaje = Column(Text)
    leida = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class SolicitudNotaInterna(Base):
    __tablename__ = "solicitudes_notas_internas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_credito.id", ondelete="CASCADE"), nullable=False)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class UsuarioCliente(Base):
    __tablename__ = "usuarios_cliente"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    token_fcm = Column(Text)
    activo = Column(Boolean, default=True)
    bloqueado = Column(Boolean, default=False)
    intentos_fallidos = Column(Integer, default=0)
    ultimo_acceso = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=_now)


class Tarjeta(Base):
    __tablename__ = "tarjetas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    numero_enmascarado = Column(String(25), nullable=False)
    marca = Column(String(20))
    linea_credito = Column(Float)
    saldo_utilizado = Column(Float)
    fecha_corte = Column(Date)
    fecha_pago = Column(Date)
    estado = Column(String(20), default="activa")
    created_at = Column(DateTime(timezone=True), default=_now)


class OperacionCliente(Base):
    __tablename__ = "operaciones_cliente"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    cod_cuenta_origen = Column(String(30))
    cod_cuenta_destino = Column(String(30))
    tipo = Column(String(20))
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), default="PEN")
    estado = Column(String(20), default="pendiente")
    cod_operacion_core = Column(String(40))
    created_at = Column(DateTime(timezone=True), default=_now)


class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    destinatario_tipo = Column(String(10), nullable=False)
    asesor_id = Column(UUID(as_uuid=True), ForeignKey("asesores.id"))
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"))
    titulo = Column(String(120), nullable=False)
    cuerpo = Column(Text)
    tipo = Column(String(40))
    data_json = Column(JSON)
    leida = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class SyncOutbox(Base):
    __tablename__ = "sync_outbox"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    entidad = Column(String(40), nullable=False)
    entidad_id = Column(UUID(as_uuid=True), nullable=False)
    operacion = Column(String(10), nullable=False)
    payload = Column(JSON, nullable=False)
    estado = Column(String(15), default="pendiente")
    intentos = Column(Integer, default=0)
    core_ref = Column(String(40))
    ultimo_error = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_now)
    procesado_at = Column(DateTime(timezone=True))


class SyncLog(Base):
    __tablename__ = "sync_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    direccion = Column(String(15), nullable=False)
    entidad = Column(String(40), nullable=False)
    referencia = Column(String(60))
    resultado = Column(String(15), nullable=False)
    detalle = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_now)
