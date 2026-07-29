"""
Shared slowapi Limiter instance.

Kept in its own module so both `app.main` and the API routers can import it
without a circular import (app.main imports the routers, and a router importing
`limiter` back from app.main would deadlock the module initialisation).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
