from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_id = Column(Integer, ForeignKey("benchmark_questions.benchmark_id"), nullable=False)
    generated_sql = Column(Text, nullable=True)
    expected_sql = Column(Text, nullable=True)
    expected_answer = Column(Text, nullable=True)
    actual_answer = Column(Text, nullable=True)
    passed = Column(Boolean, nullable=False, default=False)
    execution_time_ms = Column(Integer, nullable=True)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question_rel = relationship("BenchmarkQuestion")
