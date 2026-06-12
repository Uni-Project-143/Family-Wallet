from slowapi import Limiter
from slowapi.util import get_remote_address

# get_remote_address означає, що ми будемо лімітувати запити по IP-адресі клієнта
limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
