from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BenchmarkResultResponse(BaseModel):
    result_id: int
    benchmark_id: int
    generated_sql: Optional[str] = None
    expected_sql: Optional[str] = None
    expected_answer: Optional[str] = None
    actual_answer: Optional[str] = None
    passed: bool
    execution_time_ms: Optional[int] = None
    model_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BenchmarkSummary(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float  # e.g., 0.0 to 100.0
    average_execution_time_ms: float
    sql_accuracy: float  # percentage of correct SQL queries
    token_usage: Optional[int] = 0

class BenchmarkRunResponse(BaseModel):
    summary: BenchmarkSummary
    results: List[BenchmarkResultResponse]
