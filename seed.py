"""Script de seed para la base de datos PostgreSQL.
Ejecutar DESPUES de haber creado las tablas con database-setup.sql

Uso: pip install -r requirements.txt && python seed.py
"""

import uuid
from datetime import date, datetime, timezone
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.models import Agencia, Asesor, Cliente, Credito, CarteraDiaria, CreditoPreaprobado, UsuarioCliente


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Agencia).count() > 0:
        print("Base ya tiene datos. Omitiendo seed.")
        db.close()
        return

    # Agencias
    aq = Agencia(id=uuid.uuid4(), cod_agencia="AG001", nombre="Agencia Arequipa", region="Arequipa", lat=-16.3988, lng=-71.5369)
    cs = Agencia(id=uuid.uuid4(), cod_agencia="AG002", nombre="Agencia Cusco", region="Cusco", lat=-13.5320, lng=-71.9675)
    db.add_all([aq, cs])
    db.commit()

    # Asesores
    pw = hash_password("123456")
    e1 = Asesor(id=uuid.uuid4(), codigo_empleado="0001", nombres="Maria", apellidos="Quispe Huaman", agencia_id=aq.id, perfil="operador", password_hash=pw)
    e2 = Asesor(id=uuid.uuid4(), codigo_empleado="0002", nombres="Jose", apellidos="Mamani Flores", agencia_id=aq.id, perfil="operador", password_hash=pw)
    e3 = Asesor(id=uuid.uuid4(), codigo_empleado="0003", nombres="Rosa", apellidos="Condori Apaza", agencia_id=cs.id, perfil="supervisor", password_hash=pw)
    e4 = Asesor(id=uuid.uuid4(), codigo_empleado="9999", nombres="Admin", apellidos="Prymera", agencia_id=aq.id, perfil="administrador", password_hash=pw)
    db.add_all([e1, e2, e3, e4])
    db.commit()

    # Clientes
    c1 = Cliente(id=uuid.uuid4(), numero_documento="12345678", nombres="Carlos", apellidos="Lopez Garcia", telefono="999111000", tipo_negocio="Comercio", nombre_negocio="Bodega Lopez", ingresos_estimados=2500.00, calificacion_sbs="Normal", fecha_nacimiento=date(1990, 5, 15))
    c2 = Cliente(id=uuid.uuid4(), numero_documento="87654321", nombres="Ana", apellidos="Torres Rivas", telefono="999222111", tipo_negocio="Servicios", nombre_negocio="Salon Ana", ingresos_estimados=3500.00, calificacion_sbs="Normal", fecha_nacimiento=date(1985, 8, 22))
    c3 = Cliente(id=uuid.uuid4(), numero_documento="45678912", nombres="Luis", apellidos="Mendoza Puma", telefono="999333222", tipo_negocio="Produccion", nombre_negocio="Taller Luis", ingresos_estimados=1800.00, calificacion_sbs="CPP", fecha_nacimiento=date(1995, 12, 3))
    c4 = Cliente(id=uuid.uuid4(), numero_documento="32165498", nombres="Sofia", apellidos="Cardenas Vega", telefono="999444333", tipo_negocio="Comercio", nombre_negocio="Tienda Sofia", ingresos_estimados=5000.00, calificacion_sbs="Normal", fecha_nacimiento=date(1992, 3, 10))
    c5 = Cliente(id=uuid.uuid4(), numero_documento="11111111", nombres="Cliente", apellidos="App Banco", telefono="999555444", tipo_negocio="Comercio", nombre_negocio="Cliente App", ingresos_estimados=3000.00, calificacion_sbs="Normal", fecha_nacimiento=date(1988, 7, 20))
    db.add_all([c1, c2, c3, c4, c5])
    db.commit()

    # Credito (App Fuerza de Ventas - tabla cr_creditos)
    cred1 = Credito(id=uuid.uuid4(), cod_cuenta_credito="CR-001-2026", cliente_id=c1.id, producto="Microcredito Comercio", monto_desembolsado=8500.00, saldo_capital=5200.00, saldo_total=5300.00, dias_mora=0, estado="vigente", cuotas_total=24, cuotas_pagadas=18, tea=28.5, fecha_desembolso=date(2025, 1, 15))
    cred2 = Credito(id=uuid.uuid4(), cod_cuenta_credito="CR-002-2026", cliente_id=c2.id, producto="Credito Consumo", monto_desembolsado=3000.00, saldo_capital=1200.00, saldo_total=1220.00, dias_mora=0, estado="vigente", cuotas_total=12, cuotas_pagadas=8, tea=32.0, fecha_desembolso=date(2025, 6, 1))
    cred3 = Credito(id=uuid.uuid4(), cod_cuenta_credito="CR-003-2026", cliente_id=c3.id, producto="Microcredito Comercio", monto_desembolsado=5000.00, saldo_capital=3500.00, saldo_total=3600.00, dias_mora=15, estado="vencido", cuotas_total=18, cuotas_pagadas=10, tea=30.0, fecha_desembolso=date(2025, 3, 10))
    db.add_all([cred1, cred2, cred3])
    db.commit()

    # Credito preaprobado
    preap = CreditoPreaprobado(id=uuid.uuid4(), cliente_id=c1.id, asesor_id=e1.id, monto_maximo=12000.00, plazo_sugerido_meses=24, tea_referencial=26.5, score_confianza=85, vigente=True, fecha_calculo=date.today(), fecha_vencimiento=date(2026, 8, 1))
    db.add(preap)
    db.commit()

    # Cartera diaria
    import random
    for asesor in [e1, e2]:
        for cliente in [c1, c2, c3, c4]:
            gestiones = ["RENOVACION", "AMPLIACION", "NUEVA_SOLICITUD", "SEGUIMIENTO", "RECUPERACION_MORA", "DESERTOR"]
            prioridades = ["alta", "media", "normal"]
            item = CarteraDiaria(
                id=uuid.uuid4(), asesor_id=asesor.id, cliente_id=cliente.id, agencia_id=aq.id if asesor == e1 else cs.id,
                fecha_asignacion=date.today(), tipo_gestion=random.choice(gestiones),
                prioridad=random.choice(prioridades), score_prioridad=random.randint(0, 100),
                monto_credito=random.randint(1000, 15000),
            )
            db.add(item)
    db.commit()

    # Usuario cliente (para app_cliente_Prymera)
    uc = UsuarioCliente(id=uuid.uuid4(), cliente_id=c5.id, username="11111111", password_hash=pw, activo=True)
    db.add(uc)
    db.commit()

    print("Seed completado exitosamente!")
    print("Credenciales:")
    print("  Asesores: EMP001/EMP002/EMP003/ADMIN | password: Prymera2024")
    print("  Cliente App: usuario: 11111111 | password: Prymera2024")
    db.close()


if __name__ == "__main__":
    seed()
