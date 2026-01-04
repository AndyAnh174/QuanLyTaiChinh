"""
Access Code Authentication API endpoints
"""
from ninja import Router
from django.http import JsonResponse
from django.core.cache import cache
from typing import Optional
from pydantic import BaseModel
from ..models import AccessCode

router = Router(tags=["auth"])


class AccessCodeVerify(BaseModel):
    code: str


class AccessCodeChange(BaseModel):
    old_code: str
    new_code: str


@router.post("/verify", summary="Verify access code")
def verify_access_code(request, data: AccessCodeVerify):
    """
    Verify access code and return success status.
    Implements rate limiting to prevent brute force attacks.
    """
    # Rate limiting: max 5 attempts per IP per 15 minutes
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f"access_code_attempts:{ip_address}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:
        return JsonResponse({
            "success": False,
            "error": "Too many failed attempts. Please try again in 15 minutes."
        }, status=429)
    
    # Verify code
    is_valid = AccessCode.verify_code(data.code)
    
    if is_valid:
        # Reset attempts on success
        cache.delete(cache_key)
        # Store verification in session
        request.session['access_code_verified'] = True
        request.session.set_expiry(86400)  # 24 hours
        
        return JsonResponse({
            "success": True,
            "message": "Access code verified successfully"
        })
    else:
        # Increment attempts
        cache.set(cache_key, attempts + 1, 900)  # 15 minutes TTL
        
        return JsonResponse({
            "success": False,
            "error": "Invalid access code",
            "attempts_remaining": 5 - (attempts + 1)
        }, status=401)


@router.post("/change", summary="Change access code")
def change_access_code(request, data: AccessCodeChange):
    """
    Change access code. Requires old code for verification.
    """
    # Check if old code is valid
    if not AccessCode.verify_code(data.old_code):
        return JsonResponse({
            "success": False,
            "error": "Invalid old access code"
        }, status=401)
    
    # Validate new code (minimum length)
    if len(data.new_code) < 4:
        return JsonResponse({
            "success": False,
            "error": "New access code must be at least 4 characters"
        }, status=400)
    
    # Set new code
    AccessCode.set_code(data.new_code)
    
    # Clear session to force re-verification
    request.session.flush()
    
    return JsonResponse({
        "success": True,
        "message": "Access code changed successfully"
    })


@router.get("/status", summary="Check access code status")
def check_access_status(request):
    """
    Check if access code is verified in current session.
    """
    is_verified = request.session.get('access_code_verified', False)
    
    return JsonResponse({
        "verified": is_verified
    })

