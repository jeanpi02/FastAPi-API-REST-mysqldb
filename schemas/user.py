# schemas/user.py

from typing import Optional
from pydantic import BaseModel

# Esquema del Charity Profile
class CharityProfileCreate(BaseModel):
    social_profile: Optional[str] = None
    description: Optional[str] = None

# Esquema del usuario
class UserCreate(BaseModel):
    name: str
    phone_number: Optional[str] = None
    email: str
    password: str
    address: Optional[str] = None
    role: str  # Este será "charity" si es una organización benéfica
    charity_profile: Optional[CharityProfileCreate] = None  # Datos de charity_profile, si aplica

from typing import Optional
from pydantic import BaseModel

# Esquema del Charity Profile
class CharityProfileCreate(BaseModel):
    social_profile: Optional[str] = None
    description: Optional[str] = None

# Esquema del usuario para creación
class UserCreate(BaseModel):
    name: str
    phone_number: Optional[str] = None
    email: str
    password: str
    address: Optional[str] = None
    role: str  # Este será "charity" si es una organización benéfica
    charity_profile: Optional[CharityProfileCreate] = None  # Datos de charity_profile, si aplica

# Esquema del usuario para actualización
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = None
    charity_profile: Optional[CharityProfileCreate] = None  # Datos de charity_profile, si aplica

