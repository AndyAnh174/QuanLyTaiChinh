"""
Chat with Data API endpoints (RAG)
"""
from ninja import Router
from typing import Optional, List, Dict
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

@router.get("/sessions/{session_id}/messages", response=List[Dict], summary="Get chat history")
def get_history(request, session_id: int):
    """Get all messages for a specific session"""
    from ..models import ChatSession, ChatMessage
    from typing import List, Dict
    
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    except ChatSession.DoesNotExist:
        return []


@router.get("/sessions", response=List[Dict], summary="List all chat sessions")
def list_sessions(request):
    """List all chat sessions for sidebar history"""
    from ..models import ChatSession
    
    sessions = ChatSession.objects.all().order_by('-updated_at')
    
    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", summary="Delete a chat session")
def delete_session(request, session_id: int):
    """Delete a specific chat session"""
    from ..models import ChatSession
    
    try:
        session = ChatSession.objects.get(id=session_id)
        session.delete()
        return {"success": True}
    except ChatSession.DoesNotExist:
        return {"success": False, "error": "Session not found"}
