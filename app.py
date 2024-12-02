from fastapi import FastAPI, HTTPException
from routes.user import user_router
from routes.donation import donation_router
from routes.donation_chat import donation_chat_router
from fastapi.middleware.cors import CORSMiddleware
from routes.chat_websocket import chat_websocket_router
from routes.statistics import statistics_router
from datetime import datetime, timedelta
import jwt
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.user import users
from pydantic import BaseModel


app = FastAPI()

SECRET_KEY = "fsdfsdfsdfsdfs"

# Crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Esquema para la solicitud de login
class LoginRequest(BaseModel):
    email: str
    password: str

from pydantic import BaseModel

# Definición del esquema para recibir los datos del login
class LoginRequest(BaseModel):
    email: str
    password: str

# Ruta para generar un token
@app.post("/generate_token")
async def generate_token(request: LoginRequest):
    try:
        # Verificar si el usuario existe en la base de datos
        user_query = conn.execute(users.select().where(users.c.email == request.email)).fetchone()
        if not user_query:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Verificar si la contraseña coincide
        user = dict(user_query._mapping)
        if user["password"] != request.password:  # Comparación sencilla de contraseñas
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Generar el token
        access_token_expires = timedelta(minutes=30)  # Duración del token
        access_token = create_access_token(
            data={"sub": user["email"], "role": user["role"]}, expires_delta=access_token_expires
        )

        # Incluir el user_id en la respuesta
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],  # Incluyendo el user_id
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error en la base de datos") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Esquema para el token
class TokenRequest(BaseModel):
    token: str

@app.post("/verify_token")
async def verify_token(request: TokenRequest):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=["HS256"])
        return {"message": "Token válido", "data": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Agrega explícitamente los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Incluir routers
app.include_router(user_router, tags=["users"])
app.include_router(donation_router, tags=["donations"])
app.include_router(donation_chat_router, tags=["donation_chats"])
app.include_router(chat_websocket_router, tags=["chat_websocket"])
app.include_router(statistics_router, tags=["statistics"])


if __name__ == "__main__":
    import uvicorn

    # Usa el puerto que Render especifica en la variable de entorno `PORT`
    uvicorn.run(app, host="0.0.0.0", port= 10000)