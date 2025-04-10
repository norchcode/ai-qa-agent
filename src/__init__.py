"""
Utils module initialization.
"""
from .logger import setup_logger
from .webui import start_webui

__all__ = ['setup_logger', 'start_webui']
