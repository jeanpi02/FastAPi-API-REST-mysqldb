from fastapi import FastAPI
from routes.user import user_router
from routes.donation import donation_router
from routes.donation_chat import donation_chat_router
from fastapi.middleware.cors import CORSMiddleware
from routes.chat_websocket import chat_websocket_router
from routes.statistics import statistics_router


app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],  # Agrega explícitamente los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)



app.include_router(user_router, tags= ["users"])
app.include_router(donation_router, tags=["donations"])
app.include_router(donation_chat_router, tags=["donation_chats"])
app.include_router(chat_websocket_router, tags= ["chat_websocket"])
app.include_router(statistics_router, tags=["statistics"])