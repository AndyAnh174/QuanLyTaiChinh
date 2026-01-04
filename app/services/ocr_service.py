"""
OCR service using Gemini Vision API for receipt/image processing
"""
from typing import Dict, Any, Optional, List
from .ai_service import ai_service
from .nlp_service import nlp_service


class OCRService:
    """
    Service for extracting transaction information from receipt images
    """
    
    RECEIPT_PROMPT = """Phân tích hóa đơn/ảnh này và trích xuất các thông tin sau dưới dạng JSON:

{
  "merchant": "Tên cửa hàng/đơn vị",
  "amount": 10000,
  "date": "YYYY-MM-DD",
  "items": [
    {"name": "Tên món 1", "amount": 5000}
  ],
  "category": "Tên danh mục gợi ý",
  "description": "Mô tả ngắn gọn về hóa đơn này bằng Tiếng Việt (Ví dụ: Thanh toán tiền nước tháng 1)"
}

Quy tắc:
- Nếu giá trị không thấy, dùng null.
- Ngày tháng: chuyển về định dạng YYYY-MM-DD.
- Số tiền: chỉ lấy số, không lấy ký hiệu tiền tệ. Xử lý format Việt Nam (ví dụ 1.000 là 1000).
- Quan trọng: Trường 'description' PHẢI viết bằng Tiếng Việt."""

    def process_receipt(self, image_data: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Process receipt image and extract transaction information using Gemini
        """
        try:
            # Determine MIME type from filename
            mime_type = "image/jpeg"
            if filename:
                if filename.lower().endswith('.png'):
                    mime_type = "image/png"
                elif filename.lower().endswith('.webp'):
                    mime_type = "image/webp"
            
            # Analyze image with Gemini
            analysis_text = ai_service.analyze_image(image_data, self.RECEIPT_PROMPT, mime_type)
            
            # Parse JSON from the response
            extracted = self._parse_json_response(analysis_text)
            
            return extracted
        except Exception as e:
            print(f"Error processing receipt: {e}")
            return {
                "error": str(e),
                "merchant": None,
                "amount": 0,
                "date": None,
                "items": []
            }
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response (handling potential markdown code blocks)
        """
        import json
        import re
        from datetime import datetime
        
        try:
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'```json\s*|\s*```', '', text).strip()
            # Handle potential non-json preamble/postscript by finding the first { and last }
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                cleaned_text = cleaned_text[start:end+1]
            
            data = json.loads(cleaned_text)
            
            # Ensure required fields exist
            result = {
                "merchant": data.get("merchant", "Unknown Store"),
                "amount": data.get("amount", 0),
                "date": data.get("date"),
                "items": data.get("items", []),
                "category": data.get("category"),
                "description": data.get("description", "")
            }
            
            # Fallback for date if null
            if not result['date']:
                 result['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Sanitize amount (sometimes LLM returns strings with commas)
            if isinstance(result['amount'], str):
                try:
                    # Remove non-numeric characters except dots/commas
                    # Note: This is tricky for different locales. 
                    # Assuming standard input or what the prompt asked.
                    clean_amount = re.sub(r'[^\d.]', '', result['amount'])
                    result['amount'] = float(clean_amount)
                except:
                    result['amount'] = 0
            
            return result
            
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from AI response: {text}")
            return {
                "error": "Failed to parse AI response",
                "merchant": "Parse Error",
                "amount": 0,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "description": text[:200]
            }


# Singleton instance
ocr_service = OCRService()

