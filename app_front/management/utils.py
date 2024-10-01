from ipware import get_client_ip


def get_user_ip(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        return None
    if is_routable:
        return ip
    else:
        return ip