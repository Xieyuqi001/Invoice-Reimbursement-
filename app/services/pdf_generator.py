from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import platform

def get_chinese_font():
    system = platform.system()
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    elif system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    return None

_font_registered = False

def register_chinese_font():
    global _font_registered
    if _font_registered:
        return True
    
    font_path = get_chinese_font()
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            _font_registered = True
            return True
        except Exception:
            pass
    return False

def create_pdf(record, invoice_path: str, order_path: str, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    has_chinese_font = register_chinese_font()
    
    if has_chinese_font:
        title_font = 'ChineseFont'
        label_font = 'ChineseFont'
        text_font = 'ChineseFont'
    else:
        title_font = 'Helvetica-Bold'
        label_font = 'Helvetica-Bold'
        text_font = 'Helvetica'

    margin = 1.5 * cm

    c.setFont(title_font, 14)
    c.drawString(margin, height - 1 * cm, "发票信息")

    c.setFont(text_font, 12)
    y_pos = height - 2 * cm
    line_height = 0.8 * cm

    info_items = [
        ("姓名", record.name),
        ("学号", record.student_id),
        ("发票号", record.invoice_number),
        ("课题组名称", record.group_name or ""),
        ("对公/对私", record.payment_type or ""),
        ("其他信息", record.other_info or ""),
    ]

    for label, value in info_items:
        if value:
            c.setFont(label_font, 11)
            c.drawString(margin, y_pos, f"{label}:")
            c.setFont(text_font, 11)
            c.drawString(margin + 3.5 * cm, y_pos, str(value))
            y_pos -= line_height

    c.line(margin, y_pos, width - margin, y_pos)
    y_pos -= 0.5 * cm

    available_width = width - 2 * margin
    available_height = y_pos - margin

    if os.path.exists(invoice_path):
        try:
            img = Image.open(invoice_path)
            img_width, img_height = img.size

            scale_w = available_width / img_width
            scale_h = available_height / img_height
            scale = min(scale_w, scale_h, 1.0)

            new_width = img_width * scale
            new_height = img_height * scale

            x_pos = (width - new_width) / 2

            c.drawImage(ImageReader(img), x_pos, y_pos - new_height, width=new_width, height=new_height)
        except Exception as e:
            c.setFont(text_font, 10)
            c.drawString(margin, y_pos - 1 * cm, f"[发票图片错误: {str(e)}]")

    c.showPage()

    if os.path.exists(order_path):
        try:
            img = Image.open(order_path)
            img_width, img_height = img.size

            available_width = width - 2 * margin
            available_height = height - 2 * margin

            scale_w = available_width / img_width
            scale_h = available_height / img_height
            scale = min(scale_w, scale_h, 1.0)

            new_width = img_width * scale
            new_height = img_height * scale

            x_pos = (width - new_width) / 2
            y_pos = (height - new_height) / 2

            c.drawImage(ImageReader(img), x_pos, y_pos, width=new_width, height=new_height)
        except Exception as e:
            c.setFont(text_font, 10)
            c.drawString(margin, height - 2 * cm, f"[订单图片错误: {str(e)}]")

    c.save()
    return output_path
