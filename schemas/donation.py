# schemas/donation.py

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel
from schemas.donated_food import DonatedFoodCreate  # Importamos el esquema DonatedFoodCreate

class DonationCreate(BaseModel):
    donor_id: int  # ID del usuario que dona
    receiver_id: int  # ID del usuario que recibe (charity)
    description: str  # Descripción de la donación
    status: Optional[str] = None
    donated_foods: List[DonatedFoodCreate]  # Lista de alimentos donados
    created_at: Optional[datetime] = None  # Fecha de creación opcional

# Esquema completo para representar una donación, incluyendo los alimentos donados
class Donation(BaseModel):
    donation_id: int  # ID de la donación (generado automáticamente)
    donor_id: int  # ID del donante
    receiver_id: int  # ID del receptor
    description: str  # Descripción de la donación
    status: str
    donated_foods: List[DonatedFoodCreate]  # Lista de alimentos donados

# Modelo de datos para actualizar el estado de la donación
class DonationStatusUpdate(BaseModel):
    status: str