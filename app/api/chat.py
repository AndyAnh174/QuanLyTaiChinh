"""
Chat with Data API endpoints (RAG)
"""
from ninja import Router
from typing import Optional
from pydantic import BaseModel
from ..services.rag_service import rag_service

router = Router(tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    question: str
    session_id: Optional[int] = None


@router.post("/ask", response=ChatResponse, summary="Ask question about financial data")
def ask_question(request, data: ChatRequest):
    """
    Ask a natural language question about financial data.
    Uses RAG to query database and generate response.
    """
    try:
        result = rag_service.query_financial_data(data.question, data.session_id)
        return {
            "answer": result["answer"],
            "session_id": result["session_id"],
            "question": data.question
        }
    except Exception as e:
        return {
            "answer": f"Xin lỗi, tôi không thể trả lời câu hỏi này. Lỗi: {str(e)}",
            "question": data.question,
            "session_id": data.session_id
        }

