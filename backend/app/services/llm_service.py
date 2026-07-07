import re
import json
import httpx
from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from app.core.config import settings

def convert_messages_to_dict(messages: list) -> List[Dict[str, str]]:
    """Converts a list of mixed LangChain Messages or dictionaries to standard API dictionaries."""
    dict_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            dict_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        elif isinstance(msg, BaseMessage):
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                role = "user"
            dict_messages.append({"role": role, "content": msg.content})
        elif hasattr(msg, "role") and hasattr(msg, "content"):
            dict_messages.append({"role": getattr(msg, "role"), "content": getattr(msg, "content")})
        elif hasattr(msg, "type") and hasattr(msg, "content"):
            role = "assistant" if getattr(msg, "type") == "ai" else "user"
            dict_messages.append({"role": role, "content": getattr(msg, "content")})
        else:
            dict_messages.append({"role": "user", "content": str(msg)})
    return dict_messages

import sys

class LlmService:
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.default_provider = settings.LLM_PROVIDER.lower()
        self.default_openrouter_model = settings.OPENROUTER_MODEL
        
        # Check if we are running in unit test context (pytest)
        self.is_testing = "pytest" in sys.modules
        
        # Check mock configurations
        self.is_groq_mock = self.is_testing or (not self.groq_api_key) or self.groq_api_key == "mock-groq-key" or len(self.groq_api_key) < 10
        self.is_openrouter_mock = self.is_testing or (not self.openrouter_api_key) or self.openrouter_api_key == "mock-openrouter-key" or len(self.openrouter_api_key) < 10

    @property
    def is_mock(self) -> bool:
        """Determines if the default selected provider is in mock/offline mode."""
        if self.default_provider == "openrouter":
            return self.is_openrouter_mock
        return self.is_groq_mock

    async def invoke(self, messages: list, model: Optional[str] = None, temperature: float = 0.0, provider: Optional[str] = None) -> str:
        """Invokes the selected LLM provider (Groq or OpenRouter)."""
        active_provider = (provider or self.default_provider).lower()
        
        if active_provider == "openrouter":
            if self.is_openrouter_mock:
                raise ValueError("OpenRouterService is in mock/offline mode (missing or invalid key)")
            
            # Use configured OpenRouter model unless it looks like an OpenRouter model already passed in
            active_model = model if (model and ":" in model) else self.default_openrouter_model
            return await self._invoke_openrouter(messages, model=active_model, temperature=temperature)
            
        else: # Default is Groq
            if self.is_groq_mock:
                raise ValueError("GroqService is in mock/offline mode (missing or invalid key)")
            
            # Ensure we use an appropriate Groq model
            active_model = model or settings.SQL_GENERATION_MODEL
            # If the user passed in tencent model to Groq by mistake, fallback
            if "tencent" in active_model or ":" in active_model:
                active_model = settings.SQL_GENERATION_MODEL
                
            return await self._invoke_groq(messages, model=active_model, temperature=temperature)

    async def _invoke_groq(self, messages: list, model: str, temperature: float) -> str:
        """Invokes Groq service via ChatGroq (LangChain)."""
        llm = ChatGroq(
            model=model,
            groq_api_key=self.groq_api_key,
            temperature=temperature
        )
        response = await llm.ainvoke(messages)
        return response.content.strip()

    async def _invoke_openrouter(self, messages: list, model: str, temperature: float) -> str:
        """
        Invokes OpenRouter completions API with:
        - "stream": true for server-sent events
        - "reasoning": {"enabled": true}
        Loads and parses chunks of content and reasoning details.
        """
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Conda AI Analyst"
        }
        
        payload = {
            "model": model,
            "messages": convert_messages_to_dict(messages),
            "temperature": temperature,
            "stream": True,
            "reasoning": {"enabled": True}
        }
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        content_accumulated = []
        reasoning_accumulated = []
        
        print(f"\n--- OpenRouter Stream Start (Model: {model}) ---", flush=True)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_content = await response.aread()
                    raise RuntimeError(f"OpenRouter API error (status {response.status_code}): {err_content.decode('utf-8', errors='ignore')}")
                
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data_json = json.loads(data_str)
                            choices = data_json.get("choices", [])
                            if not choices:
                                continue
                            
                            delta = choices[0].get("delta", {})
                            
                            # Read reasoning tokens (tencent/hy3 supports this in openrouter)
                            reasoning_details = delta.get("reasoning_details") or delta.get("reasoning")
                            if reasoning_details:
                                if isinstance(reasoning_details, list):
                                    for item in reasoning_details:
                                        if isinstance(item, str):
                                            reasoning_accumulated.append(item)
                                            print(item, end="", flush=True)
                                        elif isinstance(item, dict):
                                            item_text = item.get("text") or item.get("content") or str(item)
                                            reasoning_accumulated.append(item_text)
                                            print(item_text, end="", flush=True)
                                        else:
                                            reasoning_accumulated.append(str(item))
                                            print(str(item), end="", flush=True)
                                elif isinstance(reasoning_details, dict):
                                    item_text = reasoning_details.get("text") or reasoning_details.get("content") or str(reasoning_details)
                                    reasoning_accumulated.append(item_text)
                                    print(item_text, end="", flush=True)
                                else:
                                    reasoning_str_val = str(reasoning_details)
                                    reasoning_accumulated.append(reasoning_str_val)
                                    print(reasoning_str_val, end="", flush=True)
                                
                            # Read standard completion tokens
                            content = delta.get("content")
                            if content:
                                content_accumulated.append(content)
                                print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            continue
                            
        print("\n--- OpenRouter Stream End ---\n", flush=True)
        
        # If we got reasoning, log it for backend visibility
        reasoning_str = "".join(reasoning_accumulated).strip()
        if reasoning_str:
            # We print this to stdout so the backend logs show the thinking process
            print(f"=== Model Reasoning/Thinking Process ===\n{reasoning_str}\n========================================")
            
        return "".join(content_accumulated).strip()
