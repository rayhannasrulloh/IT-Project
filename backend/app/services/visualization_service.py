import re
from typing import List, Dict, Optional

class VisualizationService:
    def generate_plotly_config(self, columns: List[str], rows: List[Dict[str, any]]) -> Optional[dict]:
        """Guesses and generates Plotly chart configs based on query data columns."""
        if not rows or len(columns) < 2:
            return None

        num_cols = []
        date_cols = []
        str_cols = []

        # Analyze data types from first row
        first_row = rows[0]
        for col in columns:
            val = first_row.get(col)
            if isinstance(val, (int, float)):
                num_cols.append(col)
            elif isinstance(val, str):
                if re.match(r'^\d{4}-\d{2}-\d{2}', val):
                    date_cols.append(col)
                else:
                    str_cols.append(col)

        if (date_cols or str_cols) and num_cols:
            x_col = date_cols[0] if date_cols else str_cols[0]
            y_col = num_cols[0]
            
            chart_type = "line" if date_cols else "bar"
            
            return {
                "type": chart_type,
                "data": [
                    {
                        "x": [r.get(x_col) for r in rows],
                        "y": [r.get(y_col) for r in rows],
                        "type": chart_type,
                        "marker": {"color": "#6366f1"}
                    }
                ],
                "layout": {
                    "title": f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                    "xaxis": {"title": x_col.replace('_', ' ').title()},
                    "yaxis": {"title": y_col.replace('_', ' ').title()},
                    "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                    "font": {"color": "#94a3b8"}
                }
            }
        
        return None
