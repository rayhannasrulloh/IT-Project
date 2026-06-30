from decimal import Decimal
from datetime import datetime, date
from typing import Any, Dict, List

def serialize_db_value(val: Any) -> Any:
    """Helper to convert Decimal or Datetime types to JSON serializable objects."""
    if isinstance(val, Decimal):
        return float(val)
    elif isinstance(val, (datetime, date)):
        return val.isoformat()
    return val

def serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serializes a single query output row dict."""
    return {col: serialize_db_value(val) for col, val in row.items()}

def serialize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serializes a list of query output row dicts."""
    return [serialize_row(row) for row in rows]
