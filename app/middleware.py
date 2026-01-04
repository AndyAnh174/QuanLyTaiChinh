"""
Middleware for Access Code protection
"""
from django.http import JsonResponse
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class AccessCodeMiddleware(MiddlewareMixin):
    """
    Middleware to check access code verification for protected views.
    Excludes API auth endpoints and admin.
    """
    
    # Paths that don't require access code
    EXCLUDED_PATHS = [
        '/api/v1/auth/verify',
        '/api/v1/auth/change',
        '/api/v1/auth/status',
        '/auth/access-code',  # Access code entry page
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        # Skip check for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return None
        
        # Skip check for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None
        
        # Check if access code is verified in session
        if not request.session.get('access_code_verified', False):
            # For API requests, return JSON error
            if request.path.startswith('/api/'):
                return JsonResponse({
                    "error": "Access code required",
                    "message": "Please verify access code first"
                }, status=403)
            # For HTML requests, redirect to access code page
            from django.shortcuts import redirect
            return redirect('/auth/access-code')
        
        return None

