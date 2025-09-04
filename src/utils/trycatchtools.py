"""装饰器处理try-catch"""
import logging
from functools import wraps


def catch_errors(log_msg=None):
    """错误捕捉装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = log_msg or f"Error in {func.__name__}"
                logging.warning(f"{error_msg}: {str(e)}")
        return wrapper
    return decorator