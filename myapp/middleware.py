# yourapp/middleware.py
from .models import Visitor

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):  # Don't track admin visits
            return self.get_response(request)

        ip = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')

        is_organic = any(domain in referer.lower() for domain in ['google', 'bing', 'yahoo'])

        if ip and not 'bot' in user_agent.lower():
            Visitor.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                is_organic=is_organic
            )

        return self.get_response(request)
