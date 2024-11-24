# routes/donation.py

from fastapi import APIRouter, HTTPException, status
from config.db import conn
from models.donation import donations
from models.user import users
from models.donated_food import donated_foods
from schemas.donation import DonationCreate, DonationStatusUpdate
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


# Crear el router para las donaciones
donation_router = APIRouter()

@donation_router.post('/create_donation')
def create_donation(donation: DonationCreate):
    """
    Crear una nueva donación con sus alimentos donados.
    """
    try:
        print("Datos de la donación recibidos:", donation.dict())  # Depuración

        # 1. Insertar la donación en la tabla `donation`
        new_donation = {
            "donor_id": donation.donor_id,
            "receiver_id": donation.receiver_id,
            "description": donation.description,
            "status": donation.status or "pendiente",  # Asignar un estado predeterminado si no se proporciona
            "created_at": datetime.now()  # Agregar la fecha y hora actuales
        }
        result = conn.execute(donations.insert().values(new_donation))

        # Obtener el ID de la donación recién creada
        donation_id = result.inserted_primary_key[0]

        # 2. Insertar los alimentos donados en la tabla `donated_food`
        for food in donation.donated_foods:
            new_donated_food = {
                "donation_id": donation_id,
                "category": food.category,
                "quantity": food.quantity,
                "unit_of_measure": food.unit_of_measure,
                "expiration_date": food.expiration_date
            }
            conn.execute(donated_foods.insert().values(new_donated_food))

        # Confirmar los cambios con un solo commit al final
        conn.commit()

        return {"message": "Donación creada exitosamente", "donation_id": donation_id}

    except SQLAlchemyError as e:
        print("Error al crear la donación:", str(e))  # Imprime el error en los logs para depuración
        # Manejar errores y lanzar excepción HTTP
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la donación y los alimentos donados: {str(e)}"
        ) from e

        
@donation_router.get('/get_received_donations/{user_id}')
def get_received_donations(user_id: int):
    """
    Obtener todas las donaciones recibidas por un usuario específico (charity).
    """
    try:
        # 1. Obtener las donaciones donde receiver_id es igual al user_id
        donation_query = donations.select().where(donations.c.receiver_id == user_id)
        donation_results = conn.execute(donation_query).fetchall()

        # Verificar si no hay donaciones recibidas
        if not donation_results:
            return {"donations": [], "message": "No se encontraron donaciones para este usuario"}

        # 2. Preparar una lista para almacenar los resultados
        received_donations = []

        # 3. Iterar sobre cada donación recibida
        for donation in donation_results:
            donation_data = dict(donation._mapping)

            # 4. Obtener los alimentos donados relacionados con esta donación
            donated_food_query = donated_foods.select().where(donated_foods.c.donation_id == donation_data["donation_id"])
            donated_food_results = conn.execute(donated_food_query).fetchall()

            # Convertir los alimentos donados en una lista de diccionarios
            donated_food_list = [dict(food._mapping) for food in donated_food_results]

            # 5. Agregar la lista de alimentos donados a la donación
            donation_data["donated_foods"] = donated_food_list

            # 6. Agregar la donación completa a la lista de resultados
            received_donations.append(donation_data)

        return {"donations": received_donations}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Error al obtener las donaciones recibidas"
        ) from e

        

@donation_router.get('/get_my_donations/{user_id}')
def get_my_donations(user_id: int):
    """
    Obtener todas las donaciones realizadas por un usuario específico, incluyendo el detalle de la organización benéfica a la que donó.
    """
    try:
        # 1. Obtener las donaciones realizadas por el usuario donde donor_id es igual al user_id
        donation_query = donations.select().where(donations.c.donor_id == user_id)
        donation_results = conn.execute(donation_query).fetchall()

        if not donation_results:
            raise HTTPException(
                status_code=404, detail="No se encontraron donaciones realizadas por este usuario"
            )

        # 2. Preparar una lista para almacenar los resultados
        user_donations = []

        # 3. Iterar sobre cada donación realizada
        for donation in donation_results:
            donation_data = dict(donation._mapping)

            # 4. Obtener los detalles de la organización benéfica (charity) a la que se realizó la donación
            charity_query = users.select().where(users.c.user_id == donation_data["receiver_id"], users.c.role == "charity")
            charity_result = conn.execute(charity_query).fetchone()

            if charity_result:
                charity_data = dict(charity_result._mapping)
                donation_data["charity_name"] = charity_data["name"]
                donation_data["charity_address"] = charity_data["address"]

            # 5. Obtener los alimentos donados relacionados con esta donación
            donated_food_query = donated_foods.select().where(donated_foods.c.donation_id == donation_data["donation_id"])
            donated_food_results = conn.execute(donated_food_query).fetchall()

            # Convertir los alimentos donados en una lista de diccionarios
            donated_food_list = [dict(food._mapping) for food in donated_food_results]

            # 6. Agregar la lista de alimentos donados a la donación
            donation_data["donated_foods"] = donated_food_list

            # 7. Agregar la donación completa a la lista de resultados
            user_donations.append(donation_data)

        return user_donations

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Error al obtener las donaciones realizadas"
        ) from e

@donation_router.put('/update_donation_status/{donation_id}')
def update_donation_status(donation_id: int, donation_update: DonationStatusUpdate):
    """
    Actualizar el estado de una donación específica.
    """
    try:
        # Verificar si la donación existe
        donation_query = donations.select().where(donations.c.donation_id == donation_id)
        donation = conn.execute(donation_query).fetchone()

        if not donation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Donación no encontrada"
            )

        # Actualizar el estado de la donación
        update_query = donations.update().where(donations.c.donation_id == donation_id).values(status=donation_update.status)
        conn.execute(update_query)
        conn.commit()

        return {"message": "Estado de la donación actualizado exitosamente"}

    except SQLAlchemyError as e:
        print("Error al actualizar el estado de la donación:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el estado de la donación"
        ) from e