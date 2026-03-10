import base64
import os
import re
from typing import Optional, Dict, Any

def _check_baidu_ocr():
    try:
        from aip import AipOcr
        return True
    except ImportError:
        return False

from app.config import BAIDU_OCR_APP_ID, BAIDU_OCR_API_KEY, BAIDU_OCR_SECRET_KEY


class OCRService:
    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        if not _check_baidu_ocr():
            print("[OCR] baidu-aip 模块不可用")
            return
        
        if BAIDU_OCR_APP_ID and BAIDU_OCR_API_KEY and BAIDU_OCR_SECRET_KEY:
            try:
                from aip import AipOcr
                self.client = AipOcr(
                    BAIDU_OCR_APP_ID,
                    BAIDU_OCR_API_KEY,
                    BAIDU_OCR_SECRET_KEY
                )
                print(f"[OCR] 客户端初始化成功")
            except Exception as e:
                print(f"[OCR] 客户端初始化失败: {e}")
        else:
            print(f"[OCR] 配置不完整: APP_ID={BAIDU_OCR_APP_ID}, API_KEY={BAIDU_OCR_API_KEY}, SECRET_KEY={'*' * len(BAIDU_OCR_SECRET_KEY) if BAIDU_OCR_SECRET_KEY else 'None'}")

    def is_available(self) -> bool:
        return self.client is not None

    def recognize_invoice(self, image_path: str) -> Dict[str, Any]:
        result = {
            "success": False,
            "invoice_number": None,
            "confidence": 0,
            "raw_text": "",
            "error": None
        }

        if not self.is_available():
            result["error"] = "OCR服务未配置，请先配置百度AI API密钥"
            return result

        if not os.path.exists(image_path):
            result["error"] = "图片文件不存在"
            return result

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            ocr_result = self.client.vatInvoice(image_data)

            if "error_code" in ocr_result:
                result["error"] = f"OCR识别失败: {ocr_result.get('error_msg', '未知错误')}"
                return result

            if "words_result" in ocr_result:
                words_result = ocr_result["words_result"]
                
                if "InvoiceNum" in words_result:
                    invoice_num = words_result["InvoiceNum"]
                    if isinstance(invoice_num, str):
                        result["invoice_number"] = invoice_num
                    elif isinstance(invoice_num, dict):
                        result["invoice_number"] = invoice_num.get("word", "")
                
                all_text = []
                for key, value in words_result.items():
                    if isinstance(value, str):
                        all_text.append(f"{key}: {value}")
                    elif isinstance(value, dict) and "word" in value:
                        all_text.append(value["word"])
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and "word" in item:
                                all_text.append(item["word"])
                result["raw_text"] = "\n".join(all_text)

            if not result["invoice_number"]:
                invoice_number = self._extract_invoice_number_from_text(result["raw_text"])
                if invoice_number:
                    result["invoice_number"] = invoice_number

            result["success"] = bool(result["invoice_number"])

        except Exception as e:
            result["error"] = f"OCR识别异常: {str(e)}"

        return result

    def recognize_general(self, image_path: str) -> Dict[str, Any]:
        result = {
            "success": False,
            "invoice_number": None,
            "confidence": 0,
            "raw_text": "",
            "error": None
        }

        if not self.is_available():
            result["error"] = "OCR服务未配置，请先配置百度AI API密钥"
            return result

        if not os.path.exists(image_path):
            result["error"] = "图片文件不存在"
            return result

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            ocr_result = self.client.basicAccurate(image_data)

            if "error_code" in ocr_result:
                result["error"] = f"OCR识别失败: {ocr_result.get('error_msg', '未知错误')}"
                return result

            if "words_result" in ocr_result:
                words = [item["word"] for item in ocr_result["words_result"]]
                result["raw_text"] = "\n".join(words)

                invoice_number = self._extract_invoice_number_from_text(result["raw_text"])
                if invoice_number:
                    result["invoice_number"] = invoice_number
                    result["success"] = True

            if not result["invoice_number"]:
                result["error"] = "未能从图片中识别出发票号码"

        except Exception as e:
            result["error"] = f"OCR识别异常: {str(e)}"

        return result

    def _extract_invoice_number_from_text(self, text: str) -> Optional[str]:
        if not text:
            return None

        patterns = [
            r'发票号码[：:]\s*(\d{8,20})',
            r'发票代码[：:]\s*\d+\s*号码[：:]\s*(\d{8,20})',
            r'No[.:：]\s*(\d{8,20})',
            r'号码[：:]\s*(\d{8,20})',
            r'\b(\d{20})\b',
            r'\b(\d{12})\b',
            r'\b(\d{10})\b',
            r'\b(\d{8})\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None


ocr_service = OCRService()
