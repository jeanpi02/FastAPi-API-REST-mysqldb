# models/user.py

from sqlalchemy import Table, Column, Integer, String
from config.db import meta, engine

# Definir la tabla `user`
users = Table(
    "users", meta,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False),
    Column("phone_number", String(20), nullable=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=True),
    Column("address", String(255), nullable=True),
    Column("role", String(50), nullable=False)
)

# Crear la tabla en la base de datos
meta.create_all(engine)
