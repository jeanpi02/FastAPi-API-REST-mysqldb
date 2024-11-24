# schemas/donated_food.py

from pydantic import BaseModel
from datetime import date

# Esquema para la creación de alimentos donados
class DonatedFoodCreate(BaseModel):
    category: str  # Nombre del alimento donado
    quantity: int  # Cantidad del alimento
    unit_of_measure: str  # Unidad de medida (ej. kg, litros, etc.)
    expiration_date: str  # Fecha de vencimiento del alimento

# Esquema completo para representar un alimento donado (en consultas)
class DonatedFood(BaseModel):
    donated_food_id: int  # ID del alimento donado (generado automáticamente)
    donation_id: int  # ID de la donación a la que pertenece
    category: str  # Nombre del alimento donado
    quantity: int  # Cantidad del alimento
    unit_of_measure: str  # Unidad de medida
    expiration_date: str  # Fecha de vencimiento del alimento
