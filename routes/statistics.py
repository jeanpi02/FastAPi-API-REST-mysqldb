# routes/statistics.py

from fastapi import APIRouter, HTTPException, status
from config.db import conn
from models.donation import donations
from models.donated_food import donated_foods
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError


# Crear el router para las estadísticas
statistics_router = APIRouter()

@statistics_router.get('/donation_status_distribution')
def get_donation_status_distribution():
    """
    Obtener la distribución de donaciones por estado.
    """
    try:
        # Consulta para agrupar las donaciones por estado y contar la cantidad
        donation_query = conn.execute(
            select(
                donations.c.status,  # Estado de la donación
                func.count(donations.c.donation_id).label("count")  # Conteo por estado
            ).group_by(donations.c.status)  # Agrupar por estado
        ).mappings().fetchall()  # Usar mappings para devolver resultados como diccionarios

        # Convertir los resultados en una lista de diccionarios
        status_distribution = [
            {"status": row["status"], "count": row["count"]} for row in donation_query
        ]

        return {"data": status_distribution}

    except SQLAlchemyError as e:
        # Capturar y devolver errores de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la distribución de donaciones por estado"
        ) from e

@statistics_router.get('/food_category_distribution')
def get_food_category_distribution():
    """
    Obtener la cantidad total de alimentos donados por categoría, considerando solo kg y litros.
    """
    try:
        # Consulta para agrupar alimentos por categoría y unidad de medida, filtrando solo kg y litros
        food_query = conn.execute(
            select(
                donated_foods.c.category,  # Categoría del alimento
                donated_foods.c.unit_of_measure,  # Unidad de medida
                func.sum(donated_foods.c.quantity).label("total_quantity")  # Suma total de cantidades
            ).where(donated_foods.c.unit_of_measure.in_(["kilogramos", "litros"]))  # Filtrar por kg y litros
            .group_by(donated_foods.c.category, donated_foods.c.unit_of_measure)  # Agrupar por categoría y unidad
        ).mappings().fetchall()

        # Convertir los resultados en una lista de diccionarios
        category_distribution = [
            {
                "category": row["category"],
                "unit_of_measure": row["unit_of_measure"],
                "total_quantity": row["total_quantity"]
            }
            for row in food_query
        ]

        return {"data": category_distribution}

    except SQLAlchemyError as e:
        # Capturar y devolver errores de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la cantidad de alimentos por categoría y unidad de medida"
        ) from e 

@statistics_router.get('/monthly_donations')
def get_monthly_donations():
    """
    Obtener la cantidad de donaciones realizadas por mes.
    """
    try:
        # Usar DATE_FORMAT para obtener el formato YYYY-MM
        query = text("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(donation_id) AS total_donations
            FROM donations
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY DATE_FORMAT(created_at, '%Y-%m')
        """)

        # Ejecutar la consulta y obtener los resultados
        result = conn.execute(query).fetchall()

        # Convertir los resultados en una lista de diccionarios accediendo por índice
        monthly_donations = [
            {"month": row[0], "total_donations": row[1]} for row in result
        ]

        return {"data": monthly_donations}

    except SQLAlchemyError as e:
        print("Error al ejecutar la consulta de donaciones mensuales:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las donaciones mensuales: {str(e)}"
        ) from e

@statistics_router.get('/top_two_donated_foods')
def get_top_two_donated_foods():
    """
    Obtener las dos categorías más donadas por cantidad, considerando kilogramos y litros.
    """
    try:
        # Consulta para agrupar alimentos por categoría y sumar las cantidades
        food_query = conn.execute(
            select(
                donated_foods.c.category,  # Categoría del alimento
                func.sum(donated_foods.c.quantity).label("total_quantity")  # Suma total de cantidades
            ).where(donated_foods.c.unit_of_measure.in_(["kilogramos", "litros"]))  # Filtrar por kilogramos y litros
            .group_by(donated_foods.c.category)  # Agrupar por categoría
            .order_by(func.sum(donated_foods.c.quantity).desc())  # Ordenar por cantidad descendente
            .limit(2)  # Limitar a las dos categorías más donadas
        ).mappings().fetchall()

        # Convertir los resultados en una lista de diccionarios
        top_two_foods = [
            {"category": row["category"], "total_quantity": row["total_quantity"]} for row in food_query
        ]

        return {"data": top_two_foods}

    except SQLAlchemyError as e:
        # Capturar y devolver errores de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las dos categorías más donadas"
        ) from e
        

@statistics_router.get('/donations_by_role')
def get_donations_by_role():
    """
    Obtener la cantidad de donaciones realizadas por rol (restaurante vs. usuario común).
    """
    try:
        # Consulta para agrupar por rol y contar las donaciones realizadas
        query = text("""
            SELECT 
                users.role, 
                COUNT(donations.donation_id) AS total_donations
            FROM donations
            INNER JOIN users ON donations.donor_id = users.user_id
            GROUP BY users.role
            ORDER BY total_donations DESC
        """)

        # Ejecutar la consulta y procesar los resultados
        result = conn.execute(query).fetchall()

        # Convertir los resultados a una lista de diccionarios
        donations_by_role = [
            {"role": row[0], "total_donations": row[1]} for row in result
        ]

        return {"data": donations_by_role}

    except SQLAlchemyError as e:
        # Capturar y manejar errores de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las donaciones realizadas por rol"
        ) from e


@statistics_router.get('/users_by_role')
def get_users_by_role():
    """
    Obtener la cantidad de usuarios registrados en la plataforma por rol.
    """
    try:
        # Consulta para agrupar usuarios por rol y contar
        query = text("""
            SELECT 
                role, 
                COUNT(user_id) AS total_users
            FROM users
            GROUP BY role
            ORDER BY total_users DESC
        """)

        # Ejecutar la consulta y procesar los resultados
        result = conn.execute(query).fetchall()

        # Convertir los resultados en una lista de diccionarios
        users_by_role = [
            {"role": row[0], "total_users": row[1]} for row in result
        ]

        return {"data": users_by_role}

    except SQLAlchemyError as e:
        # Capturar y manejar errores de la base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la cantidad de usuarios por rol"
        ) from e
