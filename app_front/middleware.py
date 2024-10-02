from app_front.management.unregister_authorization.token import check_token, create_token
from app_front.management.unregister_authorization.unregister_web_users import generate_random_name
from app_front.management.utils import get_user_ip
from legacy.models import WebUsers

class UnregisterAuthMiddleware:
    token = ''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.exists(request.session.session_key):
            response = self.get_response(request)
            return response

        token = request.COOKIES.get('ShipKZAuthorization')
        if not token:
            self.handle_no_token(request)
        else:
            self.handle_token(request, token)

        response = self.get_response(request)
        response.set_cookie('ShipKZAuthorization', self.token, max_age=60*60*24*14)
        return response

    def handle_no_token(self, request):
        new_username = generate_random_name()
        new_username = 'UNREG_' + new_username
        web_user = WebUsers.objects.create(web_username=new_username)
        user_ip = get_user_ip(request)
        new_token = create_token(username=new_username,
                                 user_id=web_user.user_id,
                                 ip=user_ip)
        self.token = new_token

    def handle_token(self, request, token):
        decoded_token = check_token(token)
        if decoded_token:
            self.token = token
        else:
            self.handle_no_token(request)


