"""
API layer for the UKNOW system.

Provides REST API endpoints and channel-specific handlers.
"""

from uknow.api.app import create_app

__all__ = ["create_app"]
