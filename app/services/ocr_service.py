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
    
    RECEIPT_PROMPT = """Analyze this receipt/image and extract the following information:

1. Merchant/Store name
2. Total amount
3. Date (if visible)
4. List of items (if available)
5. Payment method (if visible)

Return the information in a structured format. If you cannot read something, indicate it clearly."""

    def process_receipt(self, image_data: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Process receipt image and extract transaction information using Gemini 3 Flash
        
        Args:
            image_data: Image bytes
            filename: Optional filename for reference (used to determine MIME type)
        
        Returns:
            Dictionary with extracted information
        """
        try:
            # Determine MIME type from filename
            mime_type = "image/jpeg"
            if filename:
                if filename.lower().endswith('.png'):
                    mime_type = "image/png"
                elif filename.lower().endswith('.webp'):
                    mime_type = "image/webp"
            
            # Analyze image with Gemini 3 Flash (supports both vision and text)
            analysis = ai_service.analyze_image(image_data, self.RECEIPT_PROMPT, mime_type)
            
            # Parse the analysis to extract structured data
            extracted = self._parse_analysis(analysis)
            
            # Suggest category based on merchant
            if extracted.get('merchant'):
                category = nlp_service.suggest_category(
                    extracted.get('description', ''),
                    extracted.get('merchant')
                )
                if category:
                    extracted['category'] = category
            
            return extracted
        except Exception as e:
            print(f"Error processing receipt: {e}")
            return {
                "error": str(e),
                "merchant": None,
                "amount": None,
                "items": []
            }
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse Gemini Vision analysis text into structured data
        
        Args:
            analysis_text: Raw analysis from Gemini Vision
        
        Returns:
            Structured dictionary
        """
        import re
        
        result = {
            "merchant": None,
            "amount": None,
            "date": None,
            "items": [],
            "description": analysis_text[:200]  # Store first 200 chars as description
        }
        
        # Try to extract amount (look for numbers with currency symbols)
        amount_patterns = [
            r'total[:\s]+([\d,\.]+)',
            r'tổng[:\s]+([\d,\.]+)',
            r'([\d,\.]+)\s*(?:vnđ|vnd|đ)',
            r'([\d,\.]+)\s*k',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, analysis_text.lower())
            if match:
                try:
                    amount_str = match.group(1).replace(',', '').replace('.', '')
                    # Handle 'k' suffix
                    if 'k' in analysis_text.lower()[match.start():match.end()+10]:
                        result['amount'] = float(amount_str) * 1000
                    else:
                        result['amount'] = float(amount_str)
                    break
                except:
                    pass
        
        # Try to extract merchant name (usually at the top)
        lines = analysis_text.split('\n')
        if lines:
            # First non-empty line often contains merchant name
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) < 50 and not re.match(r'^[\d\s,\.]+$', line):
                    result['merchant'] = line
                    break
        
        # Try to extract date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, analysis_text)
            if match:
                result['date'] = match.group(1)
                break
        
        return result


# Singleton instance
ocr_service = OCRService()

