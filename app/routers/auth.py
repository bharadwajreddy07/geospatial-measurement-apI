from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.schemas import TokenResponse, UserCreate, UserResponse
from app.security import create_access_token
from app.services import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db=Depends(get_db)) -> UserResponse:
    return await register_user(db, payload.email, payload.password)


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(db, form.username, form.password)
    return TokenResponse(access_token=create_access_token(user.id))