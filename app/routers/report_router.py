# app/routers/report_router.py

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models import User
from app.services import report_generator

router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/pdf", response_class=StreamingResponse)
def download_pdf_report(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    transactions = user.transactions
    pdf = report_generator.generate_pdf_report(transactions, user.email)
    headers = {
        "Content-Disposition": f"attachment; filename={user.username}_report.pdf"
    }
    return StreamingResponse(pdf, media_type="application/pdf", headers=headers)


@router.get("/csv", response_class=FileResponse)
def download_csv_report(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    transactions = db.query(user.transactions.entity).filter_by(user_id=user.id).all()
    csv_path = report_generator.generate_csv_report(transactions, user.email)
    return FileResponse(path=csv_path, filename=csv_path.split("/")[-1], media_type="text/csv")