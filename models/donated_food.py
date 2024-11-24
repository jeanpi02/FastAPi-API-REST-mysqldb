# models/donated_food.py

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from config.db import meta, engine
from models.donation import donations # Importar la tabla donation para la clave foránea

# Definir la tabla `donated_food`
donated_foods = Table(
    "donated_food", meta,
    Column("donated_food_id", Integer, primary_key=True, autoincrement=True),
    Column("donation_id", Integer, ForeignKey("donations.donation_id"), nullable=False),
    Column("category", String(255), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_of_measure", String(50), nullable=False),
    Column("expiration_date", Date, nullable=False)
)

# Crear la tabla en la base de datos
meta.create_all(engine)