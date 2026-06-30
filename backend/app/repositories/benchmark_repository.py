from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.benchmark_questions import BenchmarkQuestion
from app.models.benchmark_results import BenchmarkResult

class BenchmarkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, question: str, gold_sql: str, gold_answer: Optional[str] = None) -> BenchmarkQuestion:
        bq = BenchmarkQuestion(question=question, gold_sql=gold_sql, gold_answer=gold_answer)
        self.db.add(bq)
        await self.db.commit()
        await self.db.refresh(bq)
        return bq

    async def get_all_questions(self) -> List[BenchmarkQuestion]:
        stmt = select(BenchmarkQuestion).order_by(BenchmarkQuestion.benchmark_id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_question_by_id(self, benchmark_id: int) -> Optional[BenchmarkQuestion]:
        stmt = select(BenchmarkQuestion).filter_by(benchmark_id=benchmark_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_result(
        self,
        benchmark_id: int,
        generated_sql: Optional[str],
        expected_sql: Optional[str],
        expected_answer: Optional[str],
        actual_answer: Optional[str],
        passed: bool,
        execution_time_ms: Optional[int],
        model_name: Optional[str]
    ) -> BenchmarkResult:
        result = BenchmarkResult(
            benchmark_id=benchmark_id,
            generated_sql=generated_sql,
            expected_sql=expected_sql,
            expected_answer=expected_answer,
            actual_answer=actual_answer,
            passed=passed,
            execution_time_ms=execution_time_ms,
            model_name=model_name
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_all_results(self, limit: int = 100) -> List[BenchmarkResult]:
        stmt = select(BenchmarkResult).order_by(BenchmarkResult.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
