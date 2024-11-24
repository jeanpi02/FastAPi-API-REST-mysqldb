# routes/user.py

from fastapi import APIRouter, HTTPException, status
from config.db import conn
from models.user import users
from models.charity_profile import charity_profiles
from models.donation import donations
from models.donated_food import donated_foods
from models.donation_chat import donation_chats
from models.chat_message import chat_messages
from schemas.user import UserCreate, UserUpdate
from sqlalchemy.exc import SQLAlchemyError

user_router = APIRouter()

@user_router.get('/get_users')
def get_users():
    try:
        query_result = conn.execute(users.select()).fetchall()
        users_list = [dict(row._mapping) for row in query_result]
        return users_list
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuarios"
        ) from e

@user_router.post('/create_user')
def create_user(user: UserCreate):
    try:
        new_user = {
            "name": user.name,
            "phone_number": user.phone_number,
            "email": user.email,
            "password": user.password,
            "address": user.address,
            "role": user.role
        }
        result = conn.execute(users.insert().values(new_user))
        last_inserted_id = result.inserted_primary_key[0]

        # Confirmar la creación del usuario
        conn.commit()

        # Si el usuario es 'charity', crear el perfil de caridad
        if user.role == "charity" and user.charity_profile:
            charity_data = {
                "user_id": last_inserted_id,
                "social_profile": user.charity_profile.social_profile,
                "description": user.charity_profile.description
            }
            conn.execute(charity_profiles.insert().values(charity_data))
            conn.commit()

        return {
            "message": "Usuario creado exitosamente",
            "user_id": last_inserted_id
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el usuario y/o el perfil de caridad"
        ) from e

@user_router.get('/get_user/{user_id}')
def get_user(user_id: int):
    try:
        query = users.select().where(users.c.user_id == user_id)
        user_result = conn.execute(query).fetchone()

        if user_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )

        user_data = dict(user_result._mapping)

        if user_data["role"] == "charity":
            charity_query = charity_profiles.select().where(charity_profiles.c.user_id == user_id)
            charity_result = conn.execute(charity_query).fetchone()
            if charity_result:
                user_data["charity_profile"] = dict(charity_result._mapping)

        return user_data

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al consultar el usuario"
        ) from e

@user_router.get('/get_charity_users')
def get_charity_users():
    try:
        query_result = conn.execute(users.select().where(users.c.role == 'charity')).fetchall()
        charity_users_list = []

        for user in query_result:
            user_data = dict(user._mapping)
            charity_profile_query = charity_profiles.select().where(charity_profiles.c.user_id == user_data["user_id"])
            charity_profile_result = conn.execute(charity_profile_query).fetchone()
            if charity_profile_result:
                user_data["charity_profile"] = dict(charity_profile_result._mapping)
            else:
                user_data["charity_profile"] = None
            charity_users_list.append(user_data)

        return charity_users_list

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuarios con el rol 'charity' y sus perfiles"
        ) from e

@user_router.put('/update_user/{user_id}')
def update_user(user_id: int, user: UserUpdate):
    try:
        # Depuración: Mostrar los datos que se intentan actualizar
        print(f"Actualizando usuario con ID {user_id} con datos: {user}")

        # Actualizar los datos básicos del usuario
        update_data = {
            "name": user.name,
            "phone_number": user.phone_number,
            "email": user.email,
            "password": user.password,
            "address": user.address,
            "role": user.role
        }
        conn.execute(users.update().where(users.c.user_id == user_id).values(update_data))
        conn.commit()
        print(f"Usuario con ID {user_id} actualizado en la tabla 'users'")

        # Si el rol es 'charity' y se proporciona el perfil de caridad, actualizar o crear el perfil
        if user.role == "charity" and user.charity_profile:
            # Revisar si existe un perfil de caridad para este usuario
            charity_profile_query = charity_profiles.select().where(charity_profiles.c.user_id == user_id)
            existing_charity_profile = conn.execute(charity_profile_query).fetchone()
            print(f"Perfil de caridad existente: {existing_charity_profile}")

            # Preparar los datos del perfil de caridad
            charity_data = {
                "social_profile": user.charity_profile.social_profile,
                "description": user.charity_profile.description
            }
            print(f"Datos de charity_profile a actualizar: {charity_data}")

            if existing_charity_profile:
                # Si el perfil existe, actualizarlo
                conn.execute(
                    charity_profiles.update()
                    .where(charity_profiles.c.user_id == user_id)
                    .values(charity_data)
                )
                print(f"Perfil de caridad de usuario con ID {user_id} actualizado en 'charity_profiles'")
            else:
                # Si no existe, crearlo
                charity_data["user_id"] = user_id
                conn.execute(charity_profiles.insert().values(charity_data))
                print(f"Perfil de caridad de usuario con ID {user_id} creado en 'charity_profiles'")
            conn.commit()

        return {"message": "Usuario actualizado exitosamente"}

    except SQLAlchemyError as e:
        print(f"Error SQLAlchemy al actualizar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el usuario y/o el perfil de caridad"
        ) from e

@user_router.delete('/delete_user/{user_id}')
def delete_user(user_id: int):
    """
    Eliminar un usuario específico por su ID, incluyendo registros relacionados.
    """
    try:
        print(f"Inicio de eliminación del usuario con ID: {user_id}")

        # Eliminar mensajes de chat donde el usuario es sender o receiver
        print("Eliminando mensajes de chat relacionados...")
        conn.execute(
            chat_messages.delete().where(
                (chat_messages.c.sender_id == user_id) | (chat_messages.c.receiver_id == user_id)
            )
        )
        conn.commit()

        # Obtener los IDs de las donaciones relacionadas
        print("Obteniendo IDs de donaciones relacionadas...")
        donation_ids = conn.execute(
            donations.select().where(
                (donations.c.donor_id == user_id) | (donations.c.receiver_id == user_id)
            )
        ).scalars().all()
        print(f"IDs de donaciones relacionadas: {donation_ids}")

        # Eliminar mensajes de chat asociados a los donation_chats relacionados
        if donation_ids:
            print("Eliminando mensajes en chats de donación relacionados con las donaciones del usuario...")
            related_donation_chat_ids = conn.execute(
                donation_chats.select().where(donation_chats.c.donation_id.in_(donation_ids))
            ).scalars().all()
            
            if related_donation_chat_ids:
                conn.execute(
                    chat_messages.delete().where(chat_messages.c.donation_chat_id.in_(related_donation_chat_ids))
                )
                conn.commit()

            # Eliminar chats de donación relacionados con las donaciones del usuario
            print("Eliminando chats de donación relacionados...")
            conn.execute(
                donation_chats.delete().where(donation_chats.c.donation_id.in_(donation_ids))
            )
            conn.commit()

            # Eliminar alimentos donados relacionados con estas donaciones
            print("Eliminando alimentos donados relacionados...")
            conn.execute(
                donated_foods.delete().where(donated_foods.c.donation_id.in_(donation_ids))
            )
            conn.commit()

            # Eliminar donaciones donde el usuario es donante o receptor
            print("Eliminando donaciones donde el usuario es donante o receptor...")
            conn.execute(
                donations.delete().where(
                    (donations.c.donor_id == user_id) | (donations.c.receiver_id == user_id)
                )
            )
            conn.commit()

        # Eliminar perfil de caridad si existe
        print("Eliminando perfil de caridad si existe...")
        conn.execute(
            charity_profiles.delete().where(charity_profiles.c.user_id == user_id)
        )
        conn.commit()

        # Finalmente, eliminar el usuario
        print("Eliminando el usuario...")
        conn.execute(users.delete().where(users.c.user_id == user_id))
        conn.commit()

        print("Eliminación completada con éxito.")
        return {"message": "Usuario y registros relacionados eliminados exitosamente"}

    except SQLAlchemyError as e:
        error_message = f"Error al eliminar el usuario y los registros relacionados: {str(e)}"
        print(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        ) from e



