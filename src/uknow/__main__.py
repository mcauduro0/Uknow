"""
Main entry point for running the UKNOW API server.

Usage:
    python -m uknow
    or
    uvicorn uknow.api.app:app --reload
"""

import uvicorn

from uknow.config import get_settings


def main() -> None:
    """Run the UKNOW API server."""
    settings = get_settings()

    uvicorn.run(
        "uknow.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
