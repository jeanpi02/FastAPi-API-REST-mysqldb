# models/charity_profile.py

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config.db import meta, engine
from models.user import users  # Importamos la tabla de usuario para la clave foránea

# Definir la tabla `charity_profile`
charity_profiles = Table(
    "charity_profile",
    meta,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("social_profile", String(255), nullable=True),
    Column("description", String(500), nullable=True),
)

# Crear la tabla en la base de datos
meta.create_all(engine)
