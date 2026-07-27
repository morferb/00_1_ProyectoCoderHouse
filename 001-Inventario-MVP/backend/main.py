from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, List, Optional
import os

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.exc import IntegrityError
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/inventario_ti")
engine = create_engine(DATABASE_URL)


# ==========================================
# GESTIÓN DEL CICLO DE VIDA (LIFESPAN)
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona los eventos de inicio y cierre de la aplicación.

    Args:
        app (FastAPI): Instancia de la aplicación FastAPI.

    Yields:
        None: Cede el control a la aplicación durante su tiempo de ejecución.
    """
    SQLModel.metadata.create_all(engine)
    yield


# ==========================================
# CONFIGURACIÓN DE FASTAPI Y MÉTRICAS
# ==========================================

app = FastAPI(title="MVP Inventario TI API", version="1.0.0", lifespan=lifespan)

# Instrumentación para Prometheus (expone el endpoint /metrics automáticamente)
Instrumentator().instrument(app).expose(app)


def get_session():
    """Genera una sesión de conexión hacia la base de datos PostgreSQL.

    Yields:
        Session: Instancia activa de la sesión de base de datos.
    """
    with Session(engine) as session:
        yield session


# ==========================================
# MODELOS DE BASE DE DATOS (SQLModel)
# ==========================================

class Manufacturer(SQLModel, table=True):
    """Modelo para representar los fabricantes de equipos de red y servidores."""
    __tablename__ = "manufacturers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)


class DeviceType(SQLModel, table=True):
    """Modelo para clasificar el tipo de dispositivo."""
    __tablename__ = "device_types"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)


class Location(SQLModel, table=True):
    """Modelo para registrar las ubicaciones físicas de los equipos."""
    __tablename__ = "locations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=150)
    site_code: Optional[str] = Field(default=None, max_length=50)


class Device(SQLModel, table=True):
    """Modelo central que almacena la información operativa de los activos TI."""
    __tablename__ = "devices"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hostname: str = Field(index=True, max_length=150)
    ip_address: str = Field(max_length=45)
    serial_number: str = Field(unique=True, index=True, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="Active", max_length=50)
    
    manufacturer_id: Optional[int] = Field(default=None, foreign_key="manufacturers.id")
    device_type_id: Optional[int] = Field(default=None, foreign_key="device_types.id")
    location_id: Optional[int] = Field(default=None, foreign_key="locations.id")


# ==========================================
# RUTAS AUXILIARES
# ==========================================

@app.get("/", tags=["Health"])
def read_root():
    """Endpoint raíz para verificar el estado de la API.

    Returns:
        dict: Mensaje de bienvenida y estado del servicio.
    """
    return {"message": "API de Inventario TI operando correctamente", "status": "online"}


# ==========================================
# ENDPOINTS: MANUFACTURERS
# ==========================================

@app.post("/manufacturers/", response_model=Manufacturer, tags=["Manufacturers"])
def create_manufacturer(manufacturer: Manufacturer, session: Annotated[Session, Depends(get_session)]) -> Manufacturer:
    """Registra un nuevo fabricante en el sistema.

    Args:
        manufacturer (Manufacturer): Datos del fabricante.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si ocurre un error de integridad (ej. nombre duplicado).

    Returns:
        Manufacturer: El objeto del fabricante creado.
    """
    try:
        session.add(manufacturer)
        session.commit()
        session.refresh(manufacturer)
        return manufacturer
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="El fabricante ya existe o hay un error de integridad.")

@app.get("/manufacturers/", response_model=List[Manufacturer], tags=["Manufacturers"])
def read_manufacturers(session: Annotated[Session, Depends(get_session)]) -> List[Manufacturer]:
    """Obtiene todos los fabricantes.

    Args:
        session (Session): Sesión de base de datos inyectada.

    Returns:
        List[Manufacturer]: Lista de fabricantes.
    """
    return session.exec(select(Manufacturer)).all()

@app.get("/manufacturers/{manufacturer_id}", response_model=Manufacturer, tags=["Manufacturers"])
def read_manufacturer(manufacturer_id: int, session: Annotated[Session, Depends(get_session)]) -> Manufacturer:
    """Obtiene un fabricante específico por su ID.

    Args:
        manufacturer_id (int): ID del fabricante.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el fabricante no existe.

    Returns:
        Manufacturer: El fabricante solicitado.
    """
    manufacturer = session.get(Manufacturer, manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado.")
    return manufacturer

@app.put("/manufacturers/{manufacturer_id}", response_model=Manufacturer, tags=["Manufacturers"])
def update_manufacturer(manufacturer_id: int, manufacturer_data: Manufacturer, session: Annotated[Session, Depends(get_session)]) -> Manufacturer:
    """Actualiza los datos de un fabricante existente.

    Args:
        manufacturer_id (int): ID del fabricante a actualizar.
        manufacturer_data (Manufacturer): Nuevos datos del fabricante.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el fabricante no existe o hay un error de integridad.

    Returns:
        Manufacturer: El fabricante actualizado.
    """
    db_manufacturer = session.get(Manufacturer, manufacturer_id)
    if not db_manufacturer:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado.")
    
    try:
        db_manufacturer.name = manufacturer_data.name
        session.add(db_manufacturer)
        session.commit()
        session.refresh(db_manufacturer)
        return db_manufacturer
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al actualizar.")

@app.delete("/manufacturers/{manufacturer_id}", tags=["Manufacturers"])
def delete_manufacturer(manufacturer_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Elimina un fabricante.

    Args:
        manufacturer_id (int): ID del fabricante.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el fabricante no existe o está siendo usado por un dispositivo.

    Returns:
        dict: Mensaje de confirmación.
    """
    db_manufacturer = session.get(Manufacturer, manufacturer_id)
    if not db_manufacturer:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado.")
    
    try:
        session.delete(db_manufacturer)
        session.commit()
        return {"ok": True, "message": "Fabricante eliminado."}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar porque está en uso por uno o más dispositivos.")


# ==========================================
# ENDPOINTS: DEVICE TYPES
# ==========================================

@app.post("/device-types/", response_model=DeviceType, tags=["Device Types"])
def create_device_type(device_type: DeviceType, session: Annotated[Session, Depends(get_session)]) -> DeviceType:
    """Registra un nuevo tipo de dispositivo.

    Args:
        device_type (DeviceType): Datos del tipo de dispositivo.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el tipo ya existe.

    Returns:
        DeviceType: El tipo de dispositivo creado.
    """
    try:
        session.add(device_type)
        session.commit()
        session.refresh(device_type)
        return device_type
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="El tipo de dispositivo ya existe.")

@app.get("/device-types/", response_model=List[DeviceType], tags=["Device Types"])
def read_device_types(session: Annotated[Session, Depends(get_session)]) -> List[DeviceType]:
    """Obtiene todos los tipos de dispositivos.

    Args:
        session (Session): Sesión de base de datos inyectada.

    Returns:
        List[DeviceType]: Lista de tipos.
    """
    return session.exec(select(DeviceType)).all()

@app.delete("/device-types/{type_id}", tags=["Device Types"])
def delete_device_type(type_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Elimina un tipo de dispositivo.

    Args:
        type_id (int): ID del tipo de dispositivo.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si no existe o está en uso.

    Returns:
        dict: Confirmación de borrado.
    """
    db_type = session.get(DeviceType, type_id)
    if not db_type:
        raise HTTPException(status_code=404, detail="Tipo de dispositivo no encontrado.")
    try:
        session.delete(db_type)
        session.commit()
        return {"ok": True, "message": "Tipo eliminado."}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar porque está en uso.")


# ==========================================
# ENDPOINTS: LOCATIONS
# ==========================================

@app.post("/locations/", response_model=Location, tags=["Locations"])
def create_location(location: Location, session: Annotated[Session, Depends(get_session)]) -> Location:
    """Crea una nueva ubicación.

    Args:
        location (Location): Datos de la ubicación.
        session (Session): Sesión de base de datos inyectada.

    Returns:
        Location: La ubicación creada.
    """
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

@app.get("/locations/", response_model=List[Location], tags=["Locations"])
def read_locations(session: Annotated[Session, Depends(get_session)]) -> List[Location]:
    """Obtiene todas las ubicaciones.

    Args:
        session (Session): Sesión de base de datos inyectada.

    Returns:
        List[Location]: Lista de ubicaciones.
    """
    return session.exec(select(Location)).all()

@app.delete("/locations/{location_id}", tags=["Locations"])
def delete_location(location_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Elimina una ubicación.

    Args:
        location_id (int): ID de la ubicación.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si no existe o está en uso.

    Returns:
        dict: Confirmación de borrado.
    """
    db_loc = session.get(Location, location_id)
    if not db_loc:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada.")
    try:
        session.delete(db_loc)
        session.commit()
        return {"ok": True, "message": "Ubicación eliminada."}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar porque está en uso.")


# ==========================================
# ENDPOINTS: DEVICES
# ==========================================

@app.post("/devices/", response_model=Device, tags=["Devices"])
def create_device(device: Device, session: Annotated[Session, Depends(get_session)]) -> Device:
    """Registra un nuevo dispositivo en el inventario.

    Args:
        device (Device): Información del activo de TI.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el serial está duplicado o fallan las llaves foráneas.

    Returns:
        Device: El dispositivo creado.
    """
    try:
        session.add(device)
        session.commit()
        session.refresh(device)
        return device
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Error de Integridad: Verifica que el serial_number no esté duplicado y que los IDs de manufacturer, device_type y location existan."
        )

@app.get("/devices/", response_model=List[Device], tags=["Devices"])
def read_devices(session: Annotated[Session, Depends(get_session)]) -> List[Device]:
    """Obtiene todos los dispositivos registrados.

    Args:
        session (Session): Sesión de base de datos inyectada.

    Returns:
        List[Device]: Lista de activos.
    """
    return session.exec(select(Device)).all()

@app.get("/devices/{device_id}", response_model=Device, tags=["Devices"])
def read_device(device_id: int, session: Annotated[Session, Depends(get_session)]) -> Device:
    """Obtiene un dispositivo específico.

    Args:
        device_id (int): ID del dispositivo.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el dispositivo no existe.

    Returns:
        Device: El dispositivo solicitado.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado.")
    return device

@app.put("/devices/{device_id}", response_model=Device, tags=["Devices"])
def update_device(device_id: int, device_update: Device, session: Annotated[Session, Depends(get_session)]) -> Device:
    """Actualiza la información de un dispositivo.

    Args:
        device_id (int): ID del dispositivo.
        device_update (Device): Datos nuevos.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si no existe o hay problemas de integridad.

    Returns:
        Device: Dispositivo actualizado.
    """
    db_device = session.get(Device, device_id)
    if not db_device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado.")
    
    update_data = device_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "id":
            setattr(db_device, key, value)
            
    try:
        session.add(db_device)
        session.commit()
        session.refresh(db_device)
        return db_device
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad. Revisa llaves foráneas o duplicidad de serial.")

@app.delete("/devices/{device_id}", tags=["Devices"])
def delete_device(device_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Elimina un dispositivo del inventario.

    Args:
        device_id (int): ID del dispositivo.
        session (Session): Sesión de base de datos inyectada.

    Raises:
        HTTPException: Si el dispositivo no existe.

    Returns:
        dict: Confirmación de borrado.
    """
    db_device = session.get(Device, device_id)
    if not db_device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado.")
    
    session.delete(db_device)
    session.commit()
    return {"ok": True, "message": "Dispositivo eliminado exitosamente."}