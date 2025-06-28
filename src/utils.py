import functools
import logging

def handle_errors(logger, default_error_message="An error occurred"):
    """
    Decorator for error handling and logging
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{default_error_message}: {str(e)}")
                raise  # Re-raise the exception after logging
        return wrapper
    return decorator