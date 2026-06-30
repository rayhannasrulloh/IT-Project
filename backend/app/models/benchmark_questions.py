from sqlalchemy import Column, Integer, Text
from app.core.database import Base

class BenchmarkQuestion(Base):
    __tablename__ = "benchmark_questions"

    benchmark_id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    gold_sql = Column(Text, nullable=False)
    gold_answer = Column(Text, nullable=True)
