from app.services.llm_service import LlmService
from app.core.config import settings

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.sql_model = settings.SQL_GENERATION_MODEL
        self.exp_model = settings.EXPLANATION_MODEL
        self._llm = LlmService()
        self.is_mock = self._llm.is_mock

    async def invoke(self, messages: list, model: str, temperature: float = 0.0) -> str:
        """Invokes the unified LLM service (maintaining interface compatibility)."""
        return await self._llm.invoke(messages, model=model, temperature=temperature)
