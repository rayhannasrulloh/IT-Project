import re
from typing import Optional
from langchain.schema import HumanMessage, SystemMessage
from app.services.llm_service import LlmService
from app.utils.prompts import INTENT_SYSTEM_PROMPT

class IntentService:
    def __init__(self):
        self.llm = LlmService()

    def looks_like_greeting(self, message: str) -> bool:
        """Rule-based check for greeting keywords."""
        msg = message.lower().strip()
        msg_clean = re.sub(r'[^\w\s]', '', msg).strip()
        tokens = msg_clean.split()
        if not tokens:
            return False
            
        greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
        
        # Obvious short greetings (up to 3 words)
        if tokens[0] in greetings and len(tokens) <= 3:
            return True
            
        for phrase in greetings:
            if msg_clean == phrase or msg_clean == f"{phrase} there":
                return True
        return False

    def looks_like_help(self, message: str) -> bool:
        """Rule-based check for help instructions."""
        msg = message.lower().strip()
        msg_clean = re.sub(r'[^\w\s]', '', msg).strip()
        if not msg_clean:
            return False
            
        help_phrases = {
            "help", "what can you do", "how does this work", 
            "example questions", "capabilities", "guide"
        }
        if msg_clean in help_phrases:
            return True
        for phrase in help_phrases:
            if phrase in msg_clean and len(msg_clean.split()) <= 5:
                return True
        return False

    def looks_like_small_talk(self, message: str) -> bool:
        """Rule-based check for casual small talk questions."""
        msg = message.lower().strip()
        msg_clean = re.sub(r'[^\w\s]', '', msg).strip()
        if not msg_clean:
            return False
            
        small_talk_phrases = {
            "how are you", "who are you", "thank you", "thanks", "nice to meet you"
        }
        if msg_clean in small_talk_phrases:
            return True
        for phrase in small_talk_phrases:
            if phrase in msg_clean and len(msg_clean.split()) <= 5:
                return True
        return False

    def looks_like_data_query(self, message: str) -> bool:
        """
        Rule-based check for schema-aware business database queries.
        Includes table names, column names, business entities, metrics, and cities.
        """
        msg = message.lower().strip()
        msg_clean = re.sub(r'[^\w\s]', '', msg).strip()
        tokens = set(msg_clean.split())

        # Schema awareness: Tables and Columns
        schema_words = {
            "customer", "customers", "product", "products", "order", "orders", 
            "payment", "payments", "order_item", "order_items", "customer_id", 
            "name", "city", "tier", "product_name", "category", "order_total", 
            "order_date", "status", "amount", "method", "quantity", "line_total",
            "cost", "unit_price", "price"
        }

        # Data Query action keywords
        data_keywords = {
            "show", "list", "count", "how many", "total", "average", "sum", "top", 
            "best", "highest", "lowest", "revenue", "sales", "profit", "group by", 
            "compare", "trend", "growth", "report", "statistics", "analytics", 
            "dashboard", "monthly", "yearly"
        }

        # Known cities & locations
        cities = {
            "surabaya", "jakarta", "new york", "chicago", "los angeles", 
            "houston", "san francisco", "ny", "la", "boston", "seattle"
        }

        # 1. Check direct intersections
        if tokens.intersection(schema_words):
            return True
        if tokens.intersection(data_keywords):
            return True
        if tokens.intersection(cities):
            return True

        # 2. Check multi-word phrase combinations
        for phrase in ["how many", "group by", "average order value", "order total", "order date"]:
            if phrase in msg_clean:
                return True

        return False

    async def detect_intent(self, message: str, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Classifies the user message into one of the supported categories:
        GREETING, SMALL_TALK, HELP, DATA_QUERY, CLARIFICATION_REPLY, UNSUPPORTED.
        Enforces the priority order:
        1. Check rule-based intent detection.
        2. If rule-based checks identify a DATA_QUERY, GREETING, or HELP, return immediately.
        3. If uncertain, fallback to LLM.
        4. Never let LLM override an obvious data query.
        """
        if not message.strip():
            return "SMALL_TALK"

        # Rule-based priority check (DATA_QUERY takes top priority to avoid override)
        if self.looks_like_data_query(message):
            return "DATA_QUERY"
        if self.looks_like_greeting(message):
            return "GREETING"
        if self.looks_like_help(message):
            return "HELP"
        if self.looks_like_small_talk(message):
            return "SMALL_TALK"

        # LLM fallback
        if self.llm.is_mock:
            return "UNSUPPORTED"

        messages = [
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Classify this message: {message}")
        ]

        try:
            raw = await self.llm.invoke(messages, model=model or "llama-3-8b-8192", temperature=0.0, provider=provider)
            label = re.sub(r'[^\w_]', '', raw.strip().upper())
            
            valid_labels = {"GREETING", "SMALL_TALK", "HELP", "DATA_QUERY", "CLARIFICATION_REPLY", "UNSUPPORTED"}
            if label in valid_labels:
                return label
            return "UNSUPPORTED"
        except Exception:
            return "UNSUPPORTED"

    async def is_data_query(self, message: str, provider: Optional[str] = None, model: Optional[str] = None) -> bool:
        """Determines if the intent requires generating SQL."""
        intent = await self.detect_intent(message, provider=provider, model=model)
        return intent == "DATA_QUERY"
