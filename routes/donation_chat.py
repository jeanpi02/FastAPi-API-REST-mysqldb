# routes/donation_chat.py
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.donation_chat import donation_chats
from schemas.donation_chat import DonationChatCreate
from models.chat_message import chat_messages
from schemas.chat_message import ChatMessageCreate
from models.donation import donations
from datetime import datetime
import logging
import pytz

donation_chat_router = APIRouter()

@donation_chat_router.post('/create_donation_chat')
def create_donation_chat(donation_chat: DonationChatCreate):
    """
    Crear un nuevo chat de donación, si no existe ya uno con los mismos donation_id y creator_id.
    """
    try:
        # Verificar si ya existe un chat de donación con el mismo donation_id y creator_id
        existing_chat = conn.execute(
            donation_chats.select()
            .where(
                donation_chats.c.donation_id == donation_chat.donation_id,
                donation_chats.c.creator_id == donation_chat.creator_id
            )
        ).fetchone()

        if existing_chat:
            return {"message": "El chat de donación ya existe", "donation_chat_id": existing_chat.donation_chat_id}

        # Asignar fecha y hora actuales en la zona horaria de Colombia si `sent_time` es None
        colombia_tz = pytz.timezone("America/Bogota")
        
        sent_time = donation_chat.created_at or datetime.now(colombia_tz)
        
        # Insertar el nuevo chat en la tabla `donation_chat`
        new_chat = {
            "donation_id": donation_chat.donation_id,
            "creator_id": donation_chat.creator_id,
            "created_at": sent_time
        }
        result = conn.execute(donation_chats.insert().values(new_chat))
        conn.commit()

        # Obtener el ID del chat recién creado
        donation_chat_id = result.lastrowid

        return {"message": "Chat de donación creado exitosamente", "donation_chat_id": donation_chat_id}

    except SQLAlchemyError as e:
        # Manejar errores y lanzar excepción HTTP
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el chat de donación: {str(e)}"
        ) from e

@donation_chat_router.get('/get_donation_chat/')
def get_donation_chat(donation_id: int = None, donation_chat_id: int = None):
    """
    Obtener un chat de donación por `donation_chat_id` o `donation_id`.
    """
    try:
        if donation_chat_id:
            # Buscar el chat por `donation_chat_id`
            query = donation_chats.select().where(donation_chats.c.donation_chat_id == donation_chat_id)
        elif donation_id:
            # Buscar el chat por `donation_id`
            query = donation_chats.select().where(donation_chats.c.donation_id == donation_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar `donation_chat_id` o `donation_id` para la consulta"
            )

        donation_chat_result = conn.execute(query).fetchone()

        if donation_chat_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat de donación no encontrado"
            )

        # Convertir el resultado a un diccionario
        chat_data = dict(donation_chat_result._mapping)
        return chat_data

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al consultar el chat de donación"
        ) from e

        
@donation_chat_router.post('/create_chat_message')
def create_chat_message(chat_message: ChatMessageCreate):
    """
    Crear un mensaje de chat, verificando que el chat de donación exista.
    """
    try:
        # Verificar si el chat de donación existe en la tabla `donation_chat`
        donation_chat = conn.execute(
            donation_chats.select().where(donation_chats.c.donation_chat_id == chat_message.donation_chat_id)
        ).fetchone()

        if not donation_chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El chat de donación especificado no existe."
            )

        # Asignar fecha y hora actuales en la zona horaria de Colombia si `sent_time` es None
        colombia_tz = pytz.timezone("America/Bogota")
        
        sent_time = chat_message.sent_time or datetime.now(colombia_tz)
        # Convertir a un formato sin zona horaria compatible con MySQL
        sent_time_naive = sent_time.replace(tzinfo=None)


        # Insertar el nuevo mensaje en la tabla `chat_message`
        new_message = {
            "donation_chat_id": chat_message.donation_chat_id,
            "sender_id": chat_message.sender_id,
            "receiver_id": chat_message.receiver_id,
            "message_value": chat_message.message_value,
            "sent_time": sent_time
        }
        result = conn.execute(chat_messages.insert().values(new_message))
        conn.commit()  # Confirmar la transacción

        # Devolver la respuesta con el ID del mensaje recién creado
        return {"message": "Mensaje de chat creado exitosamente", "chat_message_id": result.lastrowid}

    except SQLAlchemyError as e:
        logging.error(f"Error al crear el mensaje de chat: {str(e)}")
        # Manejar errores y lanzar excepción HTTP
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el mensaje de chat: {str(e)}"
        ) from e



@donation_chat_router.get('/get_donation_chat_messages/{donation_chat_id}')
def get_donation_chat_messages(donation_chat_id: int):
    """
    Obtener todos los mensajes de un chat de donación específico.
    """
    try:
        # Consultar los mensajes del chat de donación especificado
        query = chat_messages.select().where(chat_messages.c.donation_chat_id == donation_chat_id)
        result = conn.execute(query)
        messages = result.fetchall()

        # Convertir los resultados en un formato serializable
        messages_data = [
            {
                "message_id": row.message_id,
                "donation_chat_id": row.donation_chat_id,
                "sender_id": row.sender_id,
                "receiver_id": row.receiver_id,
                "message_value": row.message_value,
                "sent_time": row.sent_time
            }
            for row in messages
        ]

        # Verificar si se encontraron mensajes
        if not messages_data:
            return {"message": "No hay mensajes disponibles para este chat de donación"}

        return messages_data

    except SQLAlchemyError as e:
        # Manejar errores de la base de datos y lanzar excepción HTTP
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los mensajes del chat de donación: {str(e)}"
        ) from e

@donation_chat_router.get('/get_user_related_chats/{user_id}')
def get_user_related_chats(user_id: int):
    """
    Obtener todos los chats relacionados con un usuario específico,
    donde el usuario sea el `donor` o `receiver` en la donación.
    """
    try:
        # Consultar todas las donaciones en las que el usuario es donante o receptor
        donation_query = donations.select().where(
            (donations.c.donor_id == user_id) | (donations.c.receiver_id == user_id)
        )
        donations_list = conn.execute(donation_query).fetchall()

        # Lista para almacenar chats relacionados
        user_chats = []

        # Procesar cada donación para obtener el chat de donación, si existe
        for donation in donations_list:
            donation_data = dict(donation._mapping)

            # Obtener el chat de donación para esta donación si existe
            chat_query = donation_chats.select().where(donation_chats.c.donation_id == donation_data["donation_id"])
            chat = conn.execute(chat_query).fetchone()

            if chat:
                chat_data = dict(chat._mapping)
                chat_data["donor_id"] = donation_data["donor_id"]
                chat_data["receiver_id"] = donation_data["receiver_id"]

                # Agregar el chat a la lista de chats relacionados
                user_chats.append(chat_data)

        # Devolver los chats relacionados o un mensaje si no hay chats
        if not user_chats:
            return {"chats": [], "message": "No tienes chats activos en este momento."}

        return {"chats": user_chats}

    except SQLAlchemyError as e:
        logging.error(f"Error al obtener los chats relacionados del usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los chats relacionados del usuario"
        ) from e




