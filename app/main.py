from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_chat
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

def create_app() -> FastAPI:
    """Создание и настройка приложения FastAPI"""
    
    app = FastAPI(title=settings.APP_NAME)
    
    # Настройка CORS 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
        
    app.include_router(routes_auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(routes_chat.router, prefix="/chat", tags=["chat"])
    
    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "environment": settings.ENV}
    
    return app

app = create_app()