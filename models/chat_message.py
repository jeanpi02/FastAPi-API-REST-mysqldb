from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from config.db import meta, engine

chat_messages = Table(
    "chat_message", meta,
    Column("message_id", Integer, primary_key=True, autoincrement=True),
    Column("donation_chat_id", Integer, ForeignKey("donation_chat.donation_chat_id"), nullable=False),
    Column("sender_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column("receiver_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column("message_value", String(1000), nullable=False),
    Column("sent_time", DateTime, nullable=False),
    Column("is_read", Boolean, default=False, nullable=False)
)

# Crear la tabla en la base de datos (si aún no existe)
meta.create_all(engine)