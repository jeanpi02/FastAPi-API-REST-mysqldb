# schemas/donation_chat.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Esquema para la creación de un chat de donación
class DonationChatCreate(BaseModel):
    donation_id: int  # ID de la donación asociada
    creator_id: int
    created_at: Optional[datetime]=None# ID del usuario que inicia el chat

# Esquema para representar un chat de donación completo
class DonationChat(BaseModel):
    donation_chat_id: int  # ID del chat de donación
    donation_id: int       # ID de la donación asociada
    creator_id: int        # ID del usuario que inicia el chat
    created_at: datetime   # Fecha y hora de creación del chat