﻿from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr

from app.core.config import settings
from app.services.jwt_handler import create_access_token, verify_token

router = APIRouter()

# "Banco de dados" simulado para os usuários
fake_users_db = {}


# Modelo para criaÃ§Ã£o de usuário
class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: constr(min_length=6)


# Modelo para resposta com os dados do usuário (sem a senha)
class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


# Modelo para refresh token (caso a lógica de refresh seja implementada de forma diferenciada)
class TokenRefresh(BaseModel):
    refresh_token: str


# Definição do esquema de autenticação para proteger endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    username = verify_token(token)
    if username is None or username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou usuário não encontrado",
        )
    user_data = fake_users_db[username]
    return User(email=username, full_name=user_data.get("full_name"))


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(user_create: UserCreate):
    """
    Cria um novo usuário.
    """
    if user_create.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="usuário já existe"
        )
    fake_users_db[user_create.email] = {
        "full_name": user_create.full_name,
        "password": user_create.password,  # Atenção: em produção, nunca armazene senhas em texto plano!
    }
    return User(email=user_create.email, full_name=user_create.full_name)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Valida as credenciais do usuário e retorna um token JWT.
    """
    user = fake_users_db.get(form_data.username)
    if not user or form_data.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="usuário ou senha inválidos",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retorna as informações do usuário autenticado.
    """
    return current_user


@router.post("/refresh")
def refresh_token(refresh_data: TokenRefresh):
    """
    Recebe um refresh token e retorna um novo access token.
    (Nesta implementaÃ§Ã£o simplificada, o refresh token Ã© tratado da mesma forma que o access token.
    Em cenários reais, é recomendável ter uma lógica diferenciada e armazenar os refresh tokens de forma segura.)
    """
    username = verify_token(refresh_data.refresh_token)
    if username is None or username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido"
        )

    new_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": username}, expires_delta=new_access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
