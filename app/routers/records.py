from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Record
from app.schemas import RecordResponse, RecordUpdate
from app.services.pdf_generator import create_pdf
from app.services.ocr_service import ocr_service
from typing import List, Optional
import os
import uuid
import shutil
import zipfile
from datetime import datetime
from openpyxl import Workbook

router = APIRouter()

UPLOAD_DIR = "uploads"
EXPORT_DIR = "exports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

def save_upload_file(file: UploadFile, prefix: str) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{prefix}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filepath

@router.post("/records", response_model=RecordResponse)
async def create_record(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    student_id: str = Form(...),
    invoice_number: str = Form(...),
    group_name: Optional[str] = Form("丘陵课题组"),
    payment_type: Optional[str] = Form("对公"),
    other_info: Optional[str] = Form(None),
    invoice_image: UploadFile = File(...),
    order_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Record).filter(Record.invoice_number == invoice_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="发票号已存在")

    invoice_path = save_upload_file(invoice_image, "invoice")
    order_path = save_upload_file(order_image, "order")

    record = Record(
        name=name,
        student_id=student_id,
        invoice_number=invoice_number,
        group_name=group_name,
        payment_type=payment_type,
        other_info=other_info,
        invoice_image=invoice_path,
        order_image=order_path
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@router.get("/records", response_model=List[RecordResponse])
def get_records(db: Session = Depends(get_db)):
    return db.query(Record).order_by(Record.created_at.desc()).all()

@router.get("/records/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record

@router.put("/records/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    name: Optional[str] = Form(None),
    student_id: Optional[str] = Form(None),
    invoice_number: Optional[str] = Form(None),
    group_name: Optional[str] = Form(None),
    payment_type: Optional[str] = Form(None),
    other_info: Optional[str] = Form(None),
    invoice_image: Optional[UploadFile] = File(None),
    order_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if invoice_number and invoice_number != record.invoice_number:
        existing = db.query(Record).filter(Record.invoice_number == invoice_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="发票号已存在")
        record.invoice_number = invoice_number

    if name:
        record.name = name
    if student_id:
        record.student_id = student_id
    if group_name is not None:
        record.group_name = group_name
    if payment_type is not None:
        record.payment_type = payment_type
    if other_info is not None:
        record.other_info = other_info

    if invoice_image:
        if os.path.exists(record.invoice_image):
            os.remove(record.invoice_image)
        record.invoice_image = save_upload_file(invoice_image, "invoice")

    if order_image:
        if os.path.exists(record.order_image):
            os.remove(record.order_image)
        record.order_image = save_upload_file(order_image, "order")

    db.commit()
    db.refresh(record)
    return record

@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if os.path.exists(record.invoice_image):
        os.remove(record.invoice_image)
    if os.path.exists(record.order_image):
        os.remove(record.order_image)

    db.delete(record)
    db.commit()
    return {"message": "删除成功"}

@router.get("/records/{record_id}/preview")
def preview_record_pdf(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    pdf_filename = f"{record.invoice_number}.pdf"
    pdf_path = os.path.join(EXPORT_DIR, pdf_filename)

    create_pdf(record, record.invoice_image, record.order_image, pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={pdf_filename}"
        }
    )

@router.get("/records/{record_id}/download")
def download_record_pdf(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    pdf_filename = f"{record.invoice_number}.pdf"
    pdf_path = os.path.join(EXPORT_DIR, pdf_filename)

    create_pdf(record, record.invoice_image, record.order_image, pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_filename
    )

@router.get("/export/all")
def export_all(db: Session = Depends(get_db)):
    records = db.query(Record).all()

    if not records:
        raise HTTPException(status_code=400, detail="没有可导出的记录")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"export_{timestamp}.zip"
    zip_path = os.path.join(EXPORT_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for record in records:
            pdf_filename = f"{record.invoice_number}.pdf"
            pdf_path = os.path.join(EXPORT_DIR, f"temp_{pdf_filename}")

            create_pdf(record, record.invoice_image, record.order_image, pdf_path)

            zipf.write(pdf_path, pdf_filename)
            os.remove(pdf_path)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_filename
    )

@router.get("/export/excel")
def export_excel(db: Session = Depends(get_db)):
    records = db.query(Record).all()

    if not records:
        raise HTTPException(status_code=400, detail="没有可导出的记录")

    wb = Workbook()
    ws = wb.active
    ws.title = "发票记录"

    headers = ["ID", "姓名", "学号", "发票号", "课题组名称", "对公/对私", "其他信息", "发票图片", "订单图片", "创建时间", "更新时间"]
    ws.append(headers)

    for record in records:
        ws.append([
            record.id,
            record.name,
            record.student_id,
            record.invoice_number,
            record.group_name,
            record.payment_type,
            record.other_info,
            record.invoice_image,
            record.order_image,
            record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"records_{timestamp}.xlsx"
    excel_path = os.path.join(EXPORT_DIR, excel_filename)

    wb.save(excel_path)

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel_filename
    )

@router.post("/ocr/recognize")
async def ocr_recognize_invoice(file: UploadFile = File(...)):
    if not ocr_service.is_available():
        raise HTTPException(status_code=503, detail="OCR服务未配置，请在config.py中配置百度AI API密钥")

    temp_path = save_upload_file(file, "temp_ocr")

    try:
        result = ocr_service.recognize_invoice(temp_path)
        
        if not result["success"]:
            result = ocr_service.recognize_general(temp_path)

        return {
            "success": result["success"],
            "invoice_number": result["invoice_number"],
            "confidence": result["confidence"],
            "raw_text": result["raw_text"],
            "error": result["error"]
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/ocr/status")
def get_ocr_status():
    return {
        "available": ocr_service.is_available(),
        "message": "OCR服务已就绪" if ocr_service.is_available() else "OCR服务未配置，请在config.py中配置百度AI API密钥"
    }

@router.delete("/records/all")
def delete_all_records(db: Session = Depends(get_db)):
    records = db.query(Record).all()
    
    if not records:
        return {"message": "没有可删除的记录", "deleted_count": 0}
    
    deleted_count = len(records)
    
    for record in records:
        if os.path.exists(record.invoice_image):
            os.remove(record.invoice_image)
        if os.path.exists(record.order_image):
            os.remove(record.order_image)
        db.delete(record)
    
    db.commit()
    
    return {"message": f"成功删除 {deleted_count} 条记录", "deleted_count": deleted_count}
