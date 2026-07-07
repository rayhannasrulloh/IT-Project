from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import datetime, time
import csv
import io
from fastapi.responses import StreamingResponse
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.chat import SystemStatsResponse, QueryLogResponse, ProfileResponse, UpdateRoleRequest
from app.schemas.benchmark import BenchmarkResultResponse
from app.repositories.query_repository import QueryRepository
from app.services.benchmark_service import BenchmarkService

# Imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

router = APIRouter(prefix="/admin", tags=["Admin Operations"], dependencies=[Depends(require_admin)])

def parse_date_params(start_date: Optional[str], end_date: Optional[str]):
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            try:
                parsed_start = datetime.fromisoformat(start_date)
            except ValueError:
                pass
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d")
            parsed_end = datetime.combine(parsed_end.date(), time(23, 59, 59, 999999))
        except ValueError:
            try:
                parsed_end = datetime.fromisoformat(end_date)
            except ValueError:
                pass
    return parsed_start, parsed_end

# --- Finalized Specification Endpoints ---

@router.get("/query-logs", response_model=List[QueryLogResponse])
async def get_query_logs_final(
    limit: int = 100,
    user_email: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    query_text: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve audit log history of all compiled SQL statements across the platform with filtering."""
    parsed_start, parsed_end = parse_date_params(start_date, end_date)
    repo = QueryRepository(db)
    return await repo.get_all_logs(
        limit=limit,
        user_email=user_email,
        start_date=parsed_start,
        end_date=parsed_end,
        query_text=query_text,
        status=status
    )


@router.get("/analytics", response_model=SystemStatsResponse)
async def get_system_analytics(db: AsyncSession = Depends(get_db)):
    """Aggregate stats across profiles, conversations, queries, and documents for the admin panel."""
    repo = QueryRepository(db)
    stats = await repo.get_system_stats()
    return stats


# --- Frontend Compatibility Endpoints ---

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats_compat(db: AsyncSession = Depends(get_db)):
    """Get system stats alias for frontend."""
    repo = QueryRepository(db)
    return await repo.get_system_stats()


@router.get("/logs", response_model=List[QueryLogResponse])
async def get_query_logs_compat(
    limit: int = 100,
    user_email: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    query_text: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve audit query log history alias for frontend with filtering."""
    parsed_start, parsed_end = parse_date_params(start_date, end_date)
    repo = QueryRepository(db)
    return await repo.get_all_logs(
        limit=limit,
        user_email=user_email,
        start_date=parsed_start,
        end_date=parsed_end,
        query_text=query_text,
        status=status
    )


@router.get("/logs/export/csv")
async def export_logs_csv(
    user_email: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    query_text: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export query logs matching current filters to CSV."""
    parsed_start, parsed_end = parse_date_params(start_date, end_date)
    repo = QueryRepository(db)
    logs = await repo.get_all_logs(
        limit=10000,
        user_email=user_email,
        start_date=parsed_start,
        end_date=parsed_end,
        query_text=query_text,
        status=status
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Log ID", "User Email", "User ID", "Question / Query", 
        "Generated SQL", "Duration (ms)", "Rows Returned", "Status", "Error Message", "Timestamp"
    ])
    for log in logs:
        writer.writerow([
            log.log_id,
            log.user_email or "",
            log.user_id,
            log.question,
            log.generated_sql or "",
            log.execution_time_ms or 0,
            log.rows_returned or 0,
            log.status,
            log.error_message or "",
            log.created_at.isoformat() if log.created_at else ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=query_logs_report.csv"}
    )


@router.get("/logs/export/pdf")
async def export_logs_pdf(
    user_email: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    query_text: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export query logs matching current filters to PDF."""
    parsed_start, parsed_end = parse_date_params(start_date, end_date)
    repo = QueryRepository(db)
    logs = await repo.get_all_logs(
        limit=500,
        user_email=user_email,
        start_date=parsed_start,
        end_date=parsed_end,
        query_text=query_text,
        status=status
    )
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    from reportlab.lib.styles import ParagraphStyle
    style_normal = ParagraphStyle(
        'LogNormal',
        parent=styles['Normal'],
        fontSize=7,
        leading=9
    )
    style_title = ParagraphStyle(
        'LogTitle',
        parent=styles['Title'],
        fontSize=16,
        leading=20
    )
    
    elements = []
    elements.append(Paragraph("Conda AI Audit Logs Report", style_title))
    elements.append(Spacer(1, 10))
    
    filter_details = []
    if user_email: filter_details.append(f"Email: {user_email}")
    if start_date: filter_details.append(f"From: {start_date}")
    if end_date: filter_details.append(f"To: {end_date}")
    if query_text: filter_details.append(f"Query Search: {query_text}")
    if status: filter_details.append(f"Status: {status}")
    filter_str = ", ".join(filter_details) if filter_details else "All Logs"
    elements.append(Paragraph(f"<b>Active Filters:</b> {filter_str} | <b>Total Records:</b> {len(logs)}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    data = [["Timestamp", "User Email", "Question", "SQL Query", "Duration", "Status"]]
    for log in logs:
        time_str = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else ""
        data.append([
            time_str,
            log.user_email or "",
            Paragraph(log.question[:150], style_normal),
            Paragraph(log.generated_sql[:150] if log.generated_sql else "", style_normal),
            f"{log.execution_time_ms}ms" if log.execution_time_ms is not None else "",
            log.status
        ])
        
    t = Table(data, colWidths=[80, 90, 160, 140, 40, 30])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=query_logs_report.pdf"}
    )


@router.get("/users", response_model=List[ProfileResponse])
async def list_users(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """List all registered system users."""
    repo = QueryRepository(db)
    return await repo.get_all_profiles(limit=limit, offset=offset)


@router.put("/users/{profile_id}/role", response_model=ProfileResponse)
async def update_user_role(
    profile_id: str,
    payload: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Modify role configuration for a profile."""
    if payload.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'user'")
        
    repo = QueryRepository(db)
    updated = await repo.update_profile_role(profile_id, payload.role)
    if not updated:
        raise HTTPException(status_code=404, detail="User profile not found")
    return updated


@router.post("/benchmarks/run", response_model=List[BenchmarkResultResponse])
async def run_benchmarks_compat(db: AsyncSession = Depends(get_db)):
    """Triggers compile testing alias for frontend."""
    service = BenchmarkService(db)
    try:
        res = await service.run_benchmarks()
        return res.results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
