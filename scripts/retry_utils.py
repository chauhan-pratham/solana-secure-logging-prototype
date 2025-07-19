import time
import random
from functools import wraps
from typing import Callable, Any, Optional

class RetryConfig:
    def __init__(self, max_attempts=3, base_delay=1.0, max_delay=60.0, exponential_base=2.0, jitter=True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_on_exception(
    exceptions=(Exception,),
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
):
    """
    Decorator that retries a function on specified exceptions.
    
    Args:
        exceptions: Tuple of exceptions to catch and retry on
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # Last attempt failed, re-raise the exception
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    print(f"Attempt {attempt} failed: {e}")
                    print(f"Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception is not None:
                raise last_exception
            else:
                raise Exception("Unknown error in retry_on_exception: no exception captured.")
        
        return wrapper
    return decorator

def retry_operation(
    operation: Callable,
    *args,
    exceptions=(Exception,),
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    **kwargs
) -> Any:
    """
    Retry an operation with the specified configuration.
    
    Args:
        operation: Function to retry
        *args: Arguments to pass to the operation
        exceptions: Tuple of exceptions to catch and retry on
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        **kwargs: Keyword arguments to pass to the operation
    
    Returns:
        Result of the operation if successful
    
    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return operation(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts:
                # Last attempt failed, re-raise the exception
                raise last_exception
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
            
            # Add jitter if enabled
            if jitter:
                delay = delay * (0.5 + random.random() * 0.5)
            
            print(f"Attempt {attempt} failed: {e}")
            print(f"Retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(delay)
    
    # This should never be reached, but just in case
    if last_exception is not None:
        raise last_exception
    else:
        raise Exception("Unknown error in retry_operation: no exception captured.")

# Predefined retry configurations for common use cases
RETRY_CONFIGS = {
    'network': RetryConfig(max_attempts=5, base_delay=2.0, max_delay=30.0),
    'blockchain': RetryConfig(max_attempts=3, base_delay=5.0, max_delay=60.0),
    'file_io': RetryConfig(max_attempts=3, base_delay=1.0, max_delay=10.0),
    'quick': RetryConfig(max_attempts=2, base_delay=0.5, max_delay=5.0),
}

def retry_network(operation: Callable, *args, **kwargs) -> Any:
    """Retry operation with network-optimized settings"""
    return retry_operation(operation, *args, **kwargs, **RETRY_CONFIGS['network'].__dict__)

def retry_blockchain(operation: Callable, *args, **kwargs) -> Any:
    """Retry operation with blockchain-optimized settings"""
    return retry_operation(operation, *args, **kwargs, **RETRY_CONFIGS['blockchain'].__dict__)

def retry_file_io(operation: Callable, *args, **kwargs) -> Any:
    """Retry operation with file I/O optimized settings"""
    return retry_operation(operation, *args, **kwargs, **RETRY_CONFIGS['file_io'].__dict__) 