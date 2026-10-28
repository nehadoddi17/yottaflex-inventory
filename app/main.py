from fastapi import FastAPI, HTTPException
from app.database import check_database_connection
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.inventory_service import get_inventory_atp
from pydantic import BaseModel, Field

from app.services.movements import record_movement
from datetime import datetime

from pydantic import BaseModel, Field
from app.services.reservations import create_reservation, expire_reservations
from app.services.reconciliation import reconcile_inventory

app = FastAPI(
    title="YottaFlex Inventory Management API",
    description="Inventory tracking, reconciliation and exception management",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Inventory API is running",
    }


@app.get("/db-check")
def database_check():
    try:
        database_name = check_database_connection()
        return {
            "status": "connected",
            "database": database_name,
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check database settings.",
        )
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/inventory/atp")
def inventory_atp(
    sku_id: int,
    location_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_inventory_atp(db, sku_id, location_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) 

class MovementRequest(BaseModel):
    sku_id: int
    location_id: int
    movement_type: str
    quantity: int = Field(gt=0)


@app.post("/inventory/movements")
def create_inventory_movement(
    request: MovementRequest,
    db: Session = Depends(get_db),
):
    try:
        movement = record_movement(
            session=db,
            sku_id=request.sku_id,
            location_id=request.location_id,
            movement_type=request.movement_type,
            quantity=request.quantity,
        )

        return {
            "message": "Inventory movement recorded successfully",
            "movement_code": movement.movement_code,
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
        }

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

class ReservationRequest(BaseModel):
    order_line_id: int
    location_id: int
    quantity: int = Field(gt=0)
    expires_at: datetime


@app.post("/reservations")
def reserve_inventory(
    request: ReservationRequest,
    db: Session = Depends(get_db),
):
    try:
        reservation = create_reservation(
            session=db,
            order_line_id=request.order_line_id,
            location_id=request.location_id,
            quantity=request.quantity,
            expires_at=request.expires_at,
        )

        return {
            "message": "Reservation created successfully",
            "reservation_code": reservation.reservation_code,
            "quantity": reservation.quantity,
            "status": reservation.status,
            "expires_at": reservation.expires_at,
        }

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/reservations/expire")
def release_expired_reservations(
    db: Session = Depends(get_db),
):
    expired_count = expire_reservations(db)

    return {
        "message": "Expired reservations processed",
        "expired_count": expired_count,
    }

@app.get("/inventory/reconcile")
def reconcile_inventory_endpoint(
    sku_id: int,
    location_id: int,
    db: Session = Depends(get_db),
):
    try:
        result = reconcile_inventory(
            db,
            sku_id=sku_id,
            location_id=location_id,
        )
        return result

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


