# · Rutas de eficiencia energética: tarifas, consumos, resumen y recomendación.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.esquemas.energia import ConsumoIn, TarifaIn
from app.modelos_db import ConsumoEnergia, TarifaElectrica, get_db
from app.servicios import energia as servicio
from app.servicios.seguridad import usuario_actual

router = APIRouter(prefix="/api", dependencies=[Depends(usuario_actual)])


@router.post("/energia/tarifas")
def crear_tarifa(d: TarifaIn, db: Session = Depends(get_db)):
    return {"id": servicio.crear_tarifa(db, d).id}


@router.get("/energia/tarifas")
def listar_tarifas(db: Session = Depends(get_db)):
    return [{"id": t.id, "nombre": t.nombre, "hora_inicio": t.hora_inicio,
             "hora_fin": t.hora_fin, "valor_kwh": t.valor_kwh}
            for t in db.query(TarifaElectrica).order_by(TarifaElectrica.hora_inicio).all()]


@router.post("/energia/consumos")
def crear_consumo(d: ConsumoIn, db: Session = Depends(get_db)):
    return {"id": servicio.crear_consumo(db, d).id}


@router.get("/energia/consumos")
def listar_consumos(db: Session = Depends(get_db)):
    # · Solo los 100 más recientes.
    return [{"id": c.id, "maquina": c.maquina, "proceso": c.proceso,
             "lote": c.lote.codigo if c.lote else "", "kwh": c.kwh,
             "tarifa_kwh": c.tarifa_kwh, "costo": round(c.kwh * c.tarifa_kwh),
             "fecha": c.fecha}
            for c in db.query(ConsumoEnergia).order_by(ConsumoEnergia.id.desc()).limit(100)]


@router.get("/energia/resumen")
def energia_resumen(db: Session = Depends(get_db)):
    return servicio.resumen_energia(db)


@router.get("/energia/recomendacion")
def recomendacion(db: Session = Depends(get_db)):
    return servicio.recomendacion_energia(db)
