# routes/statistics.py

from fastapi import APIRouter, HTTPException, status
from config.db import conn
from models.donation import donations
from models.donated_food import donated_foods
from models.user import users
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Query
from datetime import date


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

@statistics_router.get('/total_donations')
def get_total_donations():
    """
    Devuelve el número total de donaciones realizadas.
    """
    try:
        # Consulta para contar las donaciones realizadas
        query = select(func.count(donations.c.donation_id).label("total_donations"))
        result = conn.execute(query).fetchone()

        # Devolver el resultado
        return {"total_donations": result.total_donations}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el total de donaciones"
        ) from e

@statistics_router.get('/total_food')
def get_total_food():
    """
    Devuelve la cantidad total de alimentos donados (kilogramos y litros).
    """
    try:
        # Consulta para sumar las cantidades de alimentos donados
        query = select(func.sum(donated_foods.c.quantity).label("total_food_quantity"))
        result = conn.execute(query).fetchone()

        # Devolver el resultado con un valor por defecto de 0
        return {"total_food_quantity": result.total_food_quantity or 0}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el total de alimentos donados"
        ) from e

@statistics_router.get('/total_users')
def get_total_users():
    """
    Devuelve el número total de usuarios registrados en la plataforma.
    """
    try:
        # Consulta para contar los usuarios registrados
        query = select(func.count().label("total_users")).select_from(users)
        result = conn.execute(query).fetchone()

        # Devolver el resultado
        return {"total_users": result.total_users}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el total de usuarios"
        ) from e

@statistics_router.get('/total_charities')
def get_total_charities():
    """
    Devuelve el número total de organizaciones benéficas registradas.
    """
    try:
        # Consulta para contar los usuarios con rol de organización benéfica
        query = select(func.count(users.c.user_id).label("total_charities")).where(users.c.role == "charity")
        result = conn.execute(query).fetchone()

        # Devolver el resultado
        return {"total_charities": result.total_charities}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el total de organizaciones benéficas"
        ) from e

@statistics_router.get('/donations_report')
def get_donations_report(start_date: date = Query(...), end_date: date = Query(...)):
    """
    Obtener un reporte de donaciones realizadas en un rango de fechas, incluyendo los nombres de donantes y receptores.
    """
    try:
        query = text("""
            SELECT 
                d.donation_id,
                u_donor.name AS donor_name,
                u_receiver.name AS receiver_name,
                d.description,
                d.status,
                d.created_at
            FROM donations d
            INNER JOIN users u_donor ON d.donor_id = u_donor.user_id
            INNER JOIN users u_receiver ON d.receiver_id = u_receiver.user_id
            WHERE d.created_at BETWEEN :start_date AND :end_date
            ORDER BY d.created_at
        """)
        result = conn.execute(query, {"start_date": start_date, "end_date": end_date}).fetchall()

        # Convertir resultados en una lista de diccionarios
        donations_report = [
            {
                "donation_id": row[0],
                "donor_name": row[1],
                "receiver_name": row[2],
                "description": row[3],
                "status": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S")
            }
            for row in result
        ]

        return {"data": donations_report}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Error al obtener el reporte de donaciones"
        ) from e

@statistics_router.get('/food_donations_report')
def get_food_donations_report(start_date: date = Query(...), end_date: date = Query(...)):
    """
    Obtener un reporte de alimentos donados por categoría en un rango de fechas.
    """
    try:
        query = text("""
            SELECT 
                donated_food.category AS category,
                donated_food.unit_of_measure AS unit_of_measure,
                SUM(donated_food.quantity) AS total_quantity
            FROM donated_food
            INNER JOIN donations ON donated_food.donation_id = donations.donation_id
            WHERE donations.created_at BETWEEN :start_date AND :end_date
            GROUP BY donated_food.category, donated_food.unit_of_measure
            ORDER BY total_quantity DESC
        """)
        result = conn.execute(query, {"start_date": start_date, "end_date": end_date}).fetchall()

        # Convertir resultados en una lista de diccionarios
        food_donations_report = [
            {
                "category": row[0],
                "unit_of_measure": row[1],
                "total_quantity": row[2]
            }
            for row in result
        ]

        return {"data": food_donations_report}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Error al obtener el reporte de alimentos donados"
        ) from e
