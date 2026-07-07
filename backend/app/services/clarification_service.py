from typing import Tuple, List, Dict, Optional

class ClarificationService:
    def __init__(self):
        # Explicit triggers matching the user prompt's ambiguity scenarios
        self.ambiguity_rules = [
            {
                "trigger": lambda q: "revenue" in q and not any(x in q for x in ["month", "product", "customer", "total", "by"]),
                "pending_intent": "revenue_analysis",
                "missing_fields": ["revenue_type"],
                "message": "Which revenue would you like to see?\n• Total revenue\n• Revenue by month\n• Revenue by product\n• Revenue by customer"
            },
            {
                "trigger": lambda q: ("sales" in q or "revenue" in q) and not any(x in q for x in ["today", "this month", "last month", "this year", "year", "period", "range", "by", "each"]),
                "pending_intent": "sales_analysis",
                "missing_fields": ["time_period"],
                "message": "For which period?\n• Today\n• This month\n• Last month\n• This year\n• Custom date range"
            },
            {
                "trigger": lambda q: "customer" in q and ("top" in q or "best" in q) and not any(x in q for x in ["spend", "order", "value", "revenue", "total"]),
                "pending_intent": "customer_ranking",
                "missing_fields": ["customer_metric"],
                "message": "What metric should I use?\n• Total spending\n• Number of orders\n• Average order value"
            },
            {
                "trigger": lambda q: "order" in q and not any(x in q for x in ["total", "status", "time", "customer", "by"]),
                "pending_intent": "order_analysis",
                "missing_fields": ["order_breakdown"],
                "message": "Would you like:\n• Total orders\n• Orders by status\n• Orders over time\n• Orders by customer"
            },
            {
                "trigger": lambda q: "product" in q and ("perform" in q or "best" in q or "top" in q) and not any(x in q for x in ["revenue", "quantity", "profit", "sold", "selling", "sales"]),
                "pending_intent": "product_performance",
                "missing_fields": ["performance_metric"],
                "message": "How would you like to measure performance?\n• Revenue\n• Quantity sold\n• Profit"
            }
        ]

    def check_ambiguity(self, query: str) -> Tuple[bool, Optional[str], List[str], Optional[str]]:
        """
        Analyzes a query string.
        Returns: (is_ambiguous, pending_intent, missing_fields, clarifying_question)
        """
        q = query.lower().strip()
        for rule in self.ambiguity_rules:
            if rule["trigger"](q):
                return True, rule["pending_intent"], rule["missing_fields"], rule["message"]
        return False, None, [], None

    def resolve_missing_field(self, pending_intent: str, user_reply: str) -> Tuple[bool, Dict[str, str]]:
        """
        Parses user reply to extract parameter values.
        Returns: (success, collected_data)
        """
        reply = user_reply.lower().strip()
        collected = {}
        
        if pending_intent == "revenue_analysis":
            if "total" in reply:
                collected["revenue_type"] = "total"
            elif "month" in reply:
                collected["revenue_type"] = "month"
            elif "product" in reply:
                collected["revenue_type"] = "product"
            elif "customer" in reply:
                collected["revenue_type"] = "customer"
                
        elif pending_intent == "sales_analysis":
            if "today" in reply:
                collected["time_period"] = "today"
            elif "this month" in reply:
                collected["time_period"] = "this month"
            elif "last month" in reply:
                collected["time_period"] = "last month"
            elif "this year" in reply or "year" in reply:
                collected["time_period"] = "this year"
                
        elif pending_intent == "customer_ranking":
            if "spending" in reply or "total spend" in reply:
                collected["customer_metric"] = "spending"
            elif "number of orders" in reply or "orders count" in reply or "orders" in reply:
                collected["customer_metric"] = "orders"
            elif "average order value" in reply or "average" in reply or "aov" in reply:
                collected["customer_metric"] = "aov"
                
        elif pending_intent == "order_analysis":
            if "total" in reply:
                collected["order_breakdown"] = "total"
            elif "status" in reply:
                collected["order_breakdown"] = "status"
            elif "over time" in reply or "time" in reply:
                collected["order_breakdown"] = "time"
            elif "customer" in reply:
                collected["order_breakdown"] = "customer"
                
        elif pending_intent == "product_performance":
            if "revenue" in reply:
                collected["performance_metric"] = "revenue"
            elif "quantity" in reply or "sold" in reply:
                collected["performance_metric"] = "quantity"
            elif "profit" in reply:
                collected["performance_metric"] = "profit"
                
        success = len(collected) > 0
        return success, collected
