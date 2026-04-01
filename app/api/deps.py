from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.repositories.chat_messages import ChatMessageRepository
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase
from app.services.openrouter_client import OpenRouterClient
from app.core.security import decode_token
from app.core.errors import NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncSession:
    """Получение сессии базы данных."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Получение репозитория пользователей."""
    return UserRepository(db)


async def get_chat_repo(db: AsyncSession = Depends(get_db)) -> ChatMessageRepository:
    """Получение репозитория сообщений."""
    return ChatMessageRepository(db)


async def get_llm_client() -> OpenRouterClient:
    """Получение клиента OpenRouter."""
    return OpenRouterClient()


async def get_auth_usecase(
    user_repo: UserRepository = Depends(get_user_repo)
) -> AuthUseCase:
    """Получение usecase аутентификации."""
    return AuthUseCase(user_repo)


async def get_chat_usecase(
    chat_repo: ChatMessageRepository = Depends(get_chat_repo),
    llm_client: OpenRouterClient = Depends(get_llm_client)
) -> ChatUseCase:
    """Получение usecase чата."""
    return ChatUseCase(chat_repo, llm_client)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int:
    """Получение ID текущего пользователя из JWT."""
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repo)
):
    """Получение текущего пользователя """
    try:
        user = await user_repo.get_by_id(user_id)
        return user
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )