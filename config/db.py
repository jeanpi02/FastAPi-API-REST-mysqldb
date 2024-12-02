from sqlalchemy import create_engine, MetaData

# Configuración de la base de datos como variables separadas
DB_USER = "uefr3vk8jkkc0orq"
DB_PASSWORD = "pV4CGXcMrdasK0HuY3Jk"
DB_HOST = "b5k0mledtralkrti6yfl-mysql.services.clever-cloud.com"
DB_PORT = 3306
DB_NAME = "b5k0mledtralkrti6yfl"

# Opción 1: Usar un diccionario para agrupar la configuración
DB_CONFIG = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_NAME,
}

# Construir la URL de la base de datos
DATABASE_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Crear la conexión a la base de datos
engine = create_engine(DATABASE_URL)
meta = MetaData()
conn = engine.connect()

print("Conexión a la base de datos exitosa")
