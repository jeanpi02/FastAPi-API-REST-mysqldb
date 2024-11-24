# models/donation.py

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, DateTime
from config.db import meta, engine
from models.user import users  # Importamos la tabla users para las claves foráneas

# Definir la tabla `donation`
donations = Table(
    "donations",
    meta,
    Column("donation_id", Integer, primary_key=True),
    Column("donor_id", Integer),
    Column("receiver_id", Integer),
    Column("description", String(255)),
    Column("status", String(50)),
    Column("created_at", DateTime),  # Verifica que esta columna exista
)

# Crear la tabla en la base de datos
meta.create_all(engine)