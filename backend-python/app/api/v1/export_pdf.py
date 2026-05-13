import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.spot_work import SpotWorkRepository
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.services.export_pdf_base import get_encoded_filename
from app.services.export_pdf_inspection import generate_periodic_inspection_pdf
from app.services.export_pdf_repair import generate_temporary_repair_pdf
from app.services.export_pdf_spotwork import generate_spot_work_pdf
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/export", tags=["PDF Export"])


@router.get("/periodic-inspection/{inspection_id}")
def export_periodic_inspection_pdf(
    inspection_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
) -> StreamingResponse:
    try:
        logger.info(f"开始导出定期巡检单PDF, inspection_id={inspection_id}")
        repo = PeriodicInspectionRepository(db)
        inspection = repo.find_by_id(inspection_id)
        if not inspection:
            raise HTTPException(status_code=404, detail="巡检单不存在")
        if inspection.status != "已完成":
            raise HTTPException(status_code=400, detail="只能导出已完成的工单")
        pdf_bytes = generate_periodic_inspection_pdf(inspection, db)
        filename = f"定期巡检单_{inspection.inspection_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": get_encoded_filename(filename)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出定期巡检单PDF失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"导出PDF失败: {str(e)}")


@router.get("/temporary-repair/{repair_id}")
def export_temporary_repair_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
) -> StreamingResponse:
    repo = TemporaryRepairRepository(db)
    repair = repo.find_by_id(repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="维修单不存在")
    if repair.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")
    pdf_bytes = generate_temporary_repair_pdf(repair, db)
    filename = f"临时维修单_{repair.repair_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )


@router.get("/spot-work/{work_id}")
def export_spot_work_pdf(
    work_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
) -> StreamingResponse:
    repo = SpotWorkRepository(db)
    work = repo.find_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="用工单不存在")
    if work.status != "已完成":
        raise HTTPException(status_code=400, detail="只能导出已完成的工单")
    pdf_bytes = generate_spot_work_pdf(work, db)
    filename = f"零星用工单_{work.work_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": get_encoded_filename(filename)}
    )
