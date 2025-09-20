import time
import logging
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Project

logger = logging.getLogger(__name__)


class ProjectMiddleware:
    """
    Middleware to handle project activation context for the Content Engine.
    Ensures that project-specific functionality works with session data.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view
        self.process_request(request)

        # info
        project_handle = request.session.get("project_handle")
        request.project = Project.objects.get("project_handle")  # type: ignore
        if project_handle is not None:
            try:
                project_obj = Project.objects.get(handle=project_handle)  # type: ignore
            except Project.DoesNotExist:  # type: ignore
                project_obj = None
            request.project = project_obj
        return self.get_response()

    def process_request(self, request):
        """Add project context to request if user is authenticated and has active project."""
        request.active_project = None

        if request.user.is_authenticated:
            project_handle = request.session.get("project_handle")
            if project_handle:
                try:
                    project = Project.objects.get(  # type: ignore
                        owner=request.user, handle=project_handle, active=True
                    )  # type: ignore
                    request.active_project = project
                except Project.DoesNotExist:  # type: ignore  # type: ignore
                    # Clean up invalid session data
                    del request.session["project_handle"]
                    logger.warning(
                        f"Invalid project handle removed from session: {project_handle}"
                    )

    def process_response(self, request, response):
        """Add project information to response headers for debugging."""
        if hasattr(request, "active_project") and request.active_project:
            response["X-Active-Project"] = request.active_project.handle
        return response


class RequestLoggingMiddleware:
    """
    Middleware to log request information and performance metrics.
    Useful for monitoring and debugging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record start time
        start_time = time.time()

        # Log request details
        logger.info(
            f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}"
        )

        # Process request
        response = self.get_response(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log response details
        logger.info(f"Response: {response.status_code} in {response_time:.3f}s")

        # Add response time header
        response["X-Response-Time"] = f"{response_time:.3f}s"

        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.
    Enhances application security.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add CSP header for static content
        if not response.get("Content-Security-Policy"):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self';"
            )

        return response


class MaintenanceModeMiddleware:
    """
    Middleware to enable maintenance mode for the application.
    Useful for deployments and updates.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is enabled (can be controlled via settings or database)
        maintenance_mode = getattr(request, "maintenance_mode", False)

        # Allow superusers to bypass maintenance mode
        if maintenance_mode and not (
            request.user.is_authenticated and request.user.is_superuser
        ):
            # Return maintenance page
            return HttpResponse(
                """
                <html>
                <head><title>Maintenance Mode</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 100px;">
                    <h1>🔧 Under Maintenance</h1>
                    <p>The Content Engine is currently undergoing maintenance.</p>
                    <p>Please check back soon!</p>
                </body>
                </html>
                """.encode(
                    "utf-8"
                ),
                status=503,
                content_type="text/html",
            )

        return self.get_response(request)


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for API endpoints.
    Prevents abuse and ensures fair usage.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.rate_limit_storage = {}  # In production, use Redis or database
        self.max_requests = 100  # requests per window
        self.window_seconds = 3600  # 1 hour window

    def process_request(self, request):
        # Only apply rate limiting to API endpoints
        if not request.path.startswith("/api/"):
            return None

        # Get client IP
        client_ip = self.get_client_ip(request)
        current_time = time.time()

        # Clean old entries
        self.cleanup_old_entries(current_time)

        # Check rate limit
        if client_ip in self.rate_limit_storage:
            requests_count = len(self.rate_limit_storage[client_ip])
            if requests_count >= self.max_requests:
                return HttpResponse(
                    "Rate limit exceeded. Try again later.".encode("utf-8"),
                    status=429,
                    content_type="text/plain",
                )

        # Record this request
        if client_ip not in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = []
        self.rate_limit_storage[client_ip].append(current_time)

        return None

    def get_client_ip(self, request):
        """Get the client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def cleanup_old_entries(self, current_time):
        """Remove entries older than the time window."""
        cutoff_time = current_time - self.window_seconds
        for ip in list(self.rate_limit_storage.keys()):
            self.rate_limit_storage[ip] = [
                timestamp
                for timestamp in self.rate_limit_storage[ip]
                if timestamp > cutoff_time
            ]
            if not self.rate_limit_storage[ip]:
                del self.rate_limit_storage[ip]


class CustomExceptionMiddleware:
    """
    Middleware to handle exceptions and provide custom error responses.
    Improves user experience during errors.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Handle exceptions and return custom error responses."""
        logger.error(f"Exception in {request.path}: {str(exception)}", exc_info=True)

        # Handle specific exceptions
        if isinstance(exception, ValueError):
            messages.error(request, "Invalid data provided. Please check your input.")
            return redirect(request.path)

        # For AJAX requests, return JSON error response
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            import json
            from django.http import JsonResponse

            return JsonResponse(
                {
                    "error": "An error occurred",
                    "message": (
                        str(exception) if settings.DEBUG else "Internal server error"
                    ),
                },
                status=500,
            )

        # Let Django handle other exceptions
        return None
