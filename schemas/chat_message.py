from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Esquema para la creación de un mensaje de chat
class ChatMessageCreate(BaseModel):
    donation_chat_id: int           # ID del chat de donación asociado
    sender_id: int                  # ID del usuario que envía el mensaje
    receiver_id: int                # ID del usuario que recibe el mensaje
    message_value: str              # Contenido del mensaje
    sent_time: Optional[datetime] = None  # Hora de envío del mensaje con valor predeterminado
    is_read: Optional[bool] = False # Estado de lectura del mensaje, predeterminado en False

# Esquema para representar un mensaje de chat completo
class ChatMessage(BaseModel):
    message_id: int                 # ID del mensaje
    donation_chat_id: int           # ID del chat de donación asociado
    sender_id: int                  # ID del usuario que envía el mensaje
    receiver_id: int                # ID del usuario que recibe el mensaje
    message_value: str              # Contenido del mensaje
    sent_time: datetime             # Hora de envío del mensaje
    is_read: bool                   # Estado de lectura del mensaje