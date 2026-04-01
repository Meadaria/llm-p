from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    """Бизнес-логика общения с LLM."""
    
    def __init__(self, chat_repo: ChatMessageRepository, llm_client: OpenRouterClient):
        self.chat_repo = chat_repo
        self.llm_client = llm_client
    
    async def ask(
        self, 
        user_id: int, 
        prompt: str, 
        system: str = None, 
        max_history: int = 10,
        temperature: float = 0.7
    ) -> str:
        """Отправить запрос к LLM и сохранить историю."""
        
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        history = await self.chat_repo.get_recent_messages(user_id, max_history)
        
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": prompt})
        
        await self.chat_repo.add_message(user_id, "user", prompt)
        
        answer = await self.llm_client.chat_completion(
            messages=messages,
            temperature=temperature
        )
        
        await self.chat_repo.add_message(user_id, "assistant", answer)
        
        return answer
    
    async def get_history(self, user_id: int) -> list:
        """Получить историю сообщений пользователя."""
        messages = await self.chat_repo.get_recent_messages(user_id, limit=100)
        return messages
    
    async def clear_history(self, user_id: int) -> None:
        """Очистить историю сообщений пользователя."""
        await self.chat_repo.delete_user_history(user_id)