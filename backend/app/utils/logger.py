import logging


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger configured by the application entry point."""
    return logging.getLogger(f"kenkomirai.{name}")
