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


class ChatResponse(BaseModel):
    answer: str
    question: str


@router.post("/ask", response=ChatResponse, summary="Ask question about financial data")
def ask_question(request, data: ChatRequest):
    """
    Ask a natural language question about financial data.
    Uses RAG to query database and generate response.
    """
    try:
        answer = rag_service.query_financial_data(data.question)
        return {
            "answer": answer,
            "question": data.question
        }
    except Exception as e:
        return {
            "answer": f"Xin lỗi, tôi không thể trả lời câu hỏi này. Lỗi: {str(e)}",
            "question": data.question
        }

