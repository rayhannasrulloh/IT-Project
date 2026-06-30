from langchain_groq import ChatGroq
from app.core.config import settings

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.is_mock = self.api_key == "mock-groq-key" or len(self.api_key) < 10
        self.sql_model = settings.SQL_GENERATION_MODEL
        self.exp_model = settings.EXPLANATION_MODEL

    async def invoke(self, messages: list, model: str, temperature: float = 0.0) -> str:
        """Invokes Groq LLM or logs/fails if in offline/mock mode."""
        if self.is_mock:
            raise ValueError("GroqService is in mock/offline mode")

        llm = ChatGroq(
            model=model,
            groq_api_key=self.api_key,
            temperature=temperature
        )
        response = await llm.ainvoke(messages)
        return response.content.strip()
