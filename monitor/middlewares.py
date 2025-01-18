from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')  # Assuming the token is stored in cookies
        if not token:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        try:
            request.user_token = AccessToken(token)  # Validates the token
        except TokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view