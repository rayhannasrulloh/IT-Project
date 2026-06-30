from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.benchmark import BenchmarkRunResponse, BenchmarkResultResponse
from app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/benchmark", tags=["SQL Compiler Benchmarks"])

@router.post("/run", response_model=BenchmarkRunResponse, dependencies=[Depends(require_admin)])
async def run_sql_benchmarks(db: AsyncSession = Depends(get_db)):
    """Triggers compile checks against a gold standard suite and generates statistics."""
    service = BenchmarkService(db)
    try:
        return await service.run_benchmarks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")


@router.get("/results", response_model=List[BenchmarkResultResponse], dependencies=[Depends(require_admin)])
async def get_sql_benchmark_results(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Retrieves list profiles of past compiler audit test records."""
    service = BenchmarkService(db)
    return await service.get_benchmark_results(limit=limit)
