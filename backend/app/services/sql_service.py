import re
import json
from typing import Tuple, List, Optional
from langchain.schema import HumanMessage, SystemMessage
from app.services.llm_service import LlmService
from app.utils.sql_validator import validate_sql_safety
from app.utils.prompts import SQL_SYSTEM_PROMPT

class SqlService:
    def __init__(self):
        self.llm = LlmService()

    async def generate_sql(
        self, 
        query_text: str, 
        chat_history: List[dict] = [], 
        provider: Optional[str] = None, 
        model: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str], str]:
        """
        Uses LLM to convert Natural Language to SQL.
        Returns: (is_ambiguous, clarification_question, sql, reasoning)
        """
        if self.llm.is_mock:
            return self._mock_sql_generation(query_text)

        messages = [
            SystemMessage(content=SQL_SYSTEM_PROMPT)
        ]
        
        # Format history context
        for msg in chat_history[-6:]:
            user_msg = msg.get("user") or msg.get("content") if msg.get("role") == "user" else ""
            assistant_msg = msg.get("analyst") or msg.get("content") if msg.get("role") == "assistant" else ""
            if user_msg:
                messages.append(HumanMessage(content=f"User: {user_msg}"))
            if assistant_msg:
                messages.append(HumanMessage(content=f"Analyst: {assistant_msg}"))
            
        messages.append(HumanMessage(content=f"Generate SQL for this question: {query_text}"))

        try:
            active_model = model or "llama-3.3-70b-versatile"
            response_content = await self.llm.invoke(messages, model=active_model, temperature=0.0, provider=provider)
            
            # Clean up JSON blocks from markdown fences
            json_match = re.search(r"```json\s*(.*?)\s*```", response_content, re.DOTALL)
            if json_match:
                response_content = json_match.group(1)
            
            parsed = json.loads(response_content)
            sql = parsed.get("sql")
            
            # Run safety checks
            if sql and not validate_sql_safety(sql):
                return False, None, None, "Safety violation: Dangerous keyword detected or not starting with SELECT/WITH."

            return (
                parsed.get("is_ambiguous", False),
                parsed.get("clarification_question"),
                sql,
                parsed.get("reasoning", "")
            )
        except Exception as e:
            print(f"LLM SQL compiling failed: {str(e)}. Falling back to rule-based mock engine.")
            return self._mock_sql_generation(query_text)

    def _mock_sql_generation(self, query_text: str) -> Tuple[bool, Optional[str], Optional[str], str]:
        qt = query_text.lower()
        
        # Custom mock outputs mapping to standard analytical requests
        if "customer" in qt and "revenue" in qt:
            sql = """SELECT c.name, SUM(oi.quantity * oi.unit_price) as revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY c.name
ORDER BY revenue DESC
LIMIT 5;"""
            return False, None, sql, "Joined customers, orders, and order items to calculate total completed order revenue per customer."

        elif "product" in qt or "selling" in qt:
            sql = """SELECT p.product_name, SUM(oi.quantity) as total_sold, SUM(oi.quantity * oi.unit_price) as total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 5;"""
            return False, None, sql, "Grouping order items by product name and summing quantities sold and revenue."

        elif "revenue" in qt or "sales" in qt:
            # Check period replies
            if "this year" in qt:
                sql = """SELECT DATE_TRUNC('month', o.order_date) as month, SUM(oi.quantity * oi.unit_price) as monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed' AND o.order_date >= '2026-01-01'
GROUP BY month
ORDER BY month ASC;"""
                return False, None, sql, "Summing order item totals for completed orders within the current year grouped by month."
            
            sql = """SELECT DATE_TRUNC('month', o.order_date) as month, SUM(oi.quantity * oi.unit_price) as monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY month
ORDER BY month ASC;"""
            return False, None, sql, "Summing completed order item totals grouped by month."

        elif "profit" in qt:
            sql = """SELECT p.product_name, SUM(oi.quantity * (oi.unit_price - p.cost)) as profit
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_name
ORDER BY profit DESC;"""
            return False, None, sql, "Calculating total unit profit per product based on purchase price and cost."

        # Default query fallback
        return False, None, "SELECT * FROM customers LIMIT 10;", "Fallback db inspection select."
