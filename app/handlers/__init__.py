# app/handlers/__init__.py
# Импорт всех роутеров


from .user import router as user_router
from .subscription import router as subscription_router
from .compatibility import router as compatibility_router
from .admin import router as admin_router

# Список всех роутеров
__all__ = ['user_router', 'subscription_router', 'compatibility_router', 'admin_router', 'routers']


routers = [
    subscription_router,
    user_router,
    compatibility_router,
    admin_router
]