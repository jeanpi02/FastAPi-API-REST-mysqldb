# routes/chat_websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.chat_message import chat_messages
from typing import List, Dict
from datetime import datetime
import pytz

chat_websocket_router = APIRouter()

# Diccionario para almacenar clientes conectados a cada chat
active_connections: Dict[int, List[WebSocket]] = {}

# Función para conectar un cliente al chat especificado
async def connect_to_chat(websocket: WebSocket, donation_chat_id: int):
    await websocket.accept()
    if donation_chat_id not in active_connections:
        active_connections[donation_chat_id] = []
    active_connections[donation_chat_id].append(websocket)

# Función para desconectar un cliente del chat
async def disconnect_from_chat(websocket: WebSocket, donation_chat_id: int):
    if donation_chat_id in active_connections:
        active_connections[donation_chat_id].remove(websocket)
        if not active_connections[donation_chat_id]:  # Eliminar entrada si no hay conexiones
            del active_connections[donation_chat_id]

# Función para enviar mensajes a todos los clientes conectados al mismo chat
async def send_message_to_chat(donation_chat_id: int, message_data: dict):
    if donation_chat_id in active_connections:
        for connection in active_connections[donation_chat_id]:
            await connection.send_json(message_data)

# Función para almacenar el mensaje en la base de datos
def save_message_to_db(message_data: dict):
    try:
        # Log de depuración antes de intentar la inserción
        print("Intentando guardar el mensaje en la base de datos...")
        print(f"Datos del mensaje: {message_data}")

        # Ejecutar la inserción directamente
        result = conn.execute(chat_messages.insert().values(message_data))
        print(f"Resultado de la inserción: {result.rowcount} fila(s) afectada(s)")

        # Confirmar los cambios con commit si `conn` es una sesión
        conn.commit()
        print("Mensaje guardado correctamente en la base de datos")

    except SQLAlchemyError as e:
        print("Error al intentar guardar el mensaje en la base de datos.")
        print(f"Detalles del error: {e}")
        conn.rollback()  # Revertir en caso de error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el mensaje en la base de datos: {str(e)}"
        ) from e

@chat_websocket_router.websocket("/ws/chat/{donation_chat_id}")
async def websocket_endpoint(websocket: WebSocket, donation_chat_id: int):
    print(f"Intentando conectar al chat con ID: {donation_chat_id}")
    await connect_to_chat(websocket, donation_chat_id)
    print(f"Cliente conectado al chat con ID: {donation_chat_id}")
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Mensaje recibido: {data}")
            colombia_tz = pytz.timezone("America/Bogota")
            sent_time = data.get("sent_time") or datetime.now(colombia_tz)

            # Quitar la zona horaria y formatear el datetime para la base de datos
            sent_time_naive = sent_time.replace(tzinfo=None)
            formatted_sent_time = sent_time_naive.strftime('%Y-%m-%d %H:%M:%S')

            message_data = {
                "donation_chat_id": donation_chat_id,
                "sender_id": data.get("sender_id"),
                "receiver_id": data.get("receiver_id"),
                "message_value": data.get("message_value"),
                "sent_time": formatted_sent_time,  # Formato sin zona horaria
                "is_read": False
            }
            
            # Guardar el mensaje en la base de datos
            print("llamando a save_message_to_db")
            save_message_to_db(message_data)
            print("Mensaje guardado en la base de datos")

            # Enviar el mensaje a todos los clientes conectados al chat
            await send_message_to_chat(donation_chat_id, message_data)
            print("Mensaje enviado a los clientes conectados")

    except WebSocketDisconnect:
        print(f"Cliente desconectado del chat con ID: {donation_chat_id}")
        await disconnect_from_chat(websocket, donation_chat_id)