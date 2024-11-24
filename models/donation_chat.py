from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from datetime import datetime
from config.db import meta, engine

# Definir la tabla `donation_chat`
donation_chats = Table(
    "donation_chat", meta,
    Column("donation_chat_id", Integer, primary_key=True, autoincrement=True),
    Column("donation_id", Integer, ForeignKey("donations.donation_id"), nullable=False, unique=True),
    Column("creator_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False) 
)

# Crear la tabla en la base de datos
meta.create_all(engine)
