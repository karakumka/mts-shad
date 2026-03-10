from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas.token import TokenRequest, TokenResponse
from src.services.token import create_access_token

token_router = APIRouter(prefix="/token", tags=["token"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@token_router.post("/", response_model=TokenResponse)
async def get_token(data: TokenRequest, session: DBSession):

    query = select(Seller).where(Seller.email == data.email)
    result = await session.execute(query)
    seller = result.scalar_one_or_none()

    if seller is None or seller.password != data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль!")

    access_token = create_access_token({"sub": str(seller.id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )