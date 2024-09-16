from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        if access_token:
            try:
                AccessToken(access_token)
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                return
            except TokenError:
                pass

        if refresh_token:
            try:
                refresh_token = RefreshToken(refresh_token)
                new_access_token = refresh_token.access_token
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                request.new_access_token = new_access_token
            except TokenError:
                pass

    def process_response(self, request, response):
        if hasattr(request, 'new_access_token'):
            access_token = request.new_access_token
            access_token_exp = access_token['exp']
            access_token_exp = timezone.datetime.fromtimestamp(
                access_token_exp,
                tz=timezone.get_current_timezone()
            )
            response.set_cookie(
                'access_token', access_token,
                expires=access_token_exp, httponly=True
            )
        return response
